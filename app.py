import streamlit as st
import streamlit.components.v1 as components
import yt_dlp
import os
import shutil
import time

# --- FUNÇÃO PARA CARREGAR CSS EXTERNO ---
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.error(f"Arquivo {file_name} não encontrado.")

# --- FUNÇÃO PARA CARREGAR JS ---
def carregar_js(file_name, nome_da_funcao):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            js_code = f.read()
            js_completo = f"""
            <script>
            {js_code}
            {nome_da_funcao}(); 
            </script>
            """
            components.html(js_completo, height=0)

# --- CONFIGURAÇÕES MESTRAS (ANTI-BLOQUEIO) ---
def get_ydl_opts(download=False, folder=None, formato=None, qualidade=None):
    # Base de opções para evitar o "Video Unavailable"
    opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        # DISFARCE: Faz o servidor do Streamlit parecer um Chrome real
        'impersonate': 'chrome', 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
    }

    # Tenta usar o arquivo de cookies se ele existir na pasta
    if os.path.exists('cookies.txt'):
        opts['cookiefile'] = 'cookies.txt'
    
    if download:
        res = "1080" if "1080p" in qualidade else "720" if "720p" in qualidade else "480"
        opts.update({
            'outtmpl': f'{folder}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        })
        
        if "MP3" in formato:
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320' if "Alta" in qualidade else '192',
                }],
            })
        else:
            opts.update({
                'format': f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best',
            })
    else:
        opts.update({
            'skip_download': True,
            'extract_flat': 'in_playlist',
        })
    return opts

# --- ETAPA 1: ANALISAR ---
def obter_info_rapido(url):
    with yt_dlp.YoutubeDL(get_ydl_opts(download=False)) as ydl:
        return ydl.extract_info(url, download=False)

# --- ETAPA 2: DOWNLOAD ---
def processar_download(url, formato, qualidade):
    folder = os.path.abspath("temp_download")
    if os.path.exists(folder): shutil.rmtree(folder)
    os.makedirs(folder)

    with yt_dlp.YoutubeDL(get_ydl_opts(True, folder, formato, qualidade)) as ydl:
        info = ydl.extract_info(url, download=True)
        return info, folder

# --- FUNÇÃO DA CAPA ---
def extrair_capa(info_dict):
    url_capa = info_dict.get("thumbnail")
    if not url_capa and info_dict.get("thumbnails"):
        url_capa = info_dict["thumbnails"][-1].get("url")
    return url_capa or "https://placehold.co/600x400?text=Sem+Capa"

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="YouTuXD Downloader", page_icon="🎥")
local_css("style.css")

if 'info_video' not in st.session_state: st.session_state.info_video = None
if 'bytes_arquivo' not in st.session_state: st.session_state.bytes_arquivo = None
if 'atirar_confete' not in st.session_state: st.session_state.atirar_confete = False

# Aviso de Cookies (Apenas para você saber se o arquivo está lá)
if not os.path.exists('cookies.txt'):
    st.warning("⚠️ Arquivo 'cookies.txt' não detectado. O YouTube pode bloquear o download no servidor.")

st.markdown("<h1>🎥 YouTuXD Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p class='stCaption'>Baixe vídeos e playlists instantaneamente.</p>", unsafe_allow_html=True)

url = st.text_input("Cole o link do YouTube:", placeholder="https://www.youtube.com/watch?v=...")
col1, col2 = st.columns(2)
with col1: tipo = st.selectbox("Formato:", ["Vídeo (MP4)", "Música (MP3)"])
with col2: qualidade = st.selectbox("Qualidade:", ["1080p (Full HD)", "720p (HD)", "480p (SD)"]) if "Vídeo" in tipo else st.selectbox("Qualidade Áudio:", ["Normal (192kbps)", "Alta (320kbps)"])

if st.button("ANALISAR LINK 🔍", use_container_width=True):
    if url:
        with st.spinner("Analisando..."):
            try:
                st.session_state.info_video = obter_info_rapido(url)
                st.session_state.bytes_arquivo = None
            except Exception as e:
                st.error(f"Erro ao analisar: {e}")

if st.session_state.info_video:
    info = st.session_state.info_video
    st.markdown(f"""
        <div class="video-card">
            <img src="{extrair_capa(info)}" class="thumbnail-img" style="width:100%; border-radius:10px;">
            <div style="padding:10px;"><b>{info.get('title')}</b></div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.bytes_arquivo is None:
        if st.button("👉 BAIXAR AGORA 👈", use_container_width=True, type="primary"):
            with st.spinner("Processando download..."):
                try:
                    info_full, pasta = processar_download(url, tipo, qualidade)
                    arquivos = [f for f in os.listdir(pasta) if not f.startswith('.')]
                    if arquivos:
                        caminho = os.path.join(pasta, arquivos[0])
                        with open(caminho, "rb") as f:
                            st.session_state.bytes_arquivo = f.read()
                            st.session_state.nome_arquivo = arquivos[0]
                        st.session_state.atirar_confete = True
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro no download: {e}")
    else:
        st.download_button("💾 SALVAR ARQUIVO", data=st.session_state.bytes_arquivo, file_name=st.session_state.nome_arquivo, use_container_width=True)
        if st.session_state.atirar_confete:
            carregar_js("script.js", "atirarConfete")
            st.session_state.atirar_confete = False

st.markdown("<div class='custom-footer'>Desenvolvido por Alessandro © 2026</div>", unsafe_allow_html=True)
