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

# --- NOVA FUNÇÃO PARA CARREGAR JS E ESCOLHER A AÇÃO ---
def carregar_js(file_name, nome_da_funcao):
    if os.path.exists(file_name):
        with open(file_name, encoding="utf-8") as f:
            js_code = f.read()
            
            # Ele lê todo o script.js, mas só executa a função que você pediu!
            js_completo = f"""
            <script>
            {js_code}
            
            // Dispara a função escolhida:
            {nome_da_funcao}(); 
            
            // Timestamp para driblar o cache: {time.time()}
            </script>
            """
            components.html(js_completo, height=0)
    else:
        st.error(f"Arquivo {file_name} não encontrado.")

# --- FUNÇÃO INFALÍVEL PARA PEGAR A CAPA ---
def extrair_capa(info_dict):
    url_capa = info_dict.get("thumbnail")
    
    if not url_capa and info_dict.get("thumbnails"):
        url_capa = info_dict["thumbnails"][-1].get("url")
        
    if not url_capa and 'entries' in info_dict and info_dict['entries']:
        for video in info_dict['entries']:
            if isinstance(video, dict):
                url_capa = video.get("thumbnail")
                if not url_capa and video.get("thumbnails"):
                    url_capa = video["thumbnails"][-1].get("url")
                if url_capa:
                    break 
                    
    if not url_capa:
        url_capa = "https://placehold.co/600x400/E5E5E5/FF0000.png?text=Sem+Capa+Disponivel"
        
    return url_capa

# Configuração da página
st.set_page_config(
    page_title="SkyDown Pro - YT Video & Playlist Loader", 
    page_icon="🎥", 
    layout="centered"
)

# Injeta o CSS
local_css("style.css")

# --- ETAPA 1: BACKEND RÁPIDO ---
def obter_info_rapido(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False,
        'ignoreerrors': True,
        'extract_flat': 'in_playlist' 
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# --- ETAPA 2: BACKEND DE DOWNLOAD ---
def processar_download(url, formato, qualidade):
    folder = "temp_download"
    if os.path.exists(folder): shutil.rmtree(folder)
    os.makedirs(folder)

    ydl_opts = {
        'outtmpl': f'{folder}/%(title)s.%(ext)s',
        'quiet': True,
        'ignoreerrors': True,
        'merge_output_format': 'mp4', 
    }

    if "MP3" in formato:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320' if "Alta" in qualidade else '192',
            }],
        })
    else:
        res = "1080" if "1080p" in qualidade else "720" if "720p" in qualidade else "480"
        ydl_opts.update({
            'format': f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best',
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info, folder

# --- INTERFACE ---
if 'info_video' not in st.session_state: st.session_state.info_video = None
if 'bytes_arquivo' not in st.session_state: st.session_state.bytes_arquivo = None
if 'nome_arquivo' not in st.session_state: st.session_state.nome_arquivo = ""
if 'fazer_scroll' not in st.session_state: st.session_state.fazer_scroll = False
if 'atirar_confete' not in st.session_state: st.session_state.atirar_confete = False # Nova memória para o confete

# Slot de Anúncio Topo
#st.markdown('<div class="ad-slot">PUBLICIDADE</div>', unsafe_allow_html=True)

# Cabeçalho Principal
st.markdown("<h1>🎥 YouTuXD Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p class='stCaption'>Baixe vídeos e playlists completas instantaneamente.</p>", unsafe_allow_html=True)

with st.container():
    url = st.text_input("Cole o link do YouTube:", placeholder="https://www.youtube.com/watch?v=...")
    
    col1, col2 = st.columns(2)
    with col1:
        tipo = st.selectbox("Formato de Saída:", ["Vídeo (MP4)", "Música (MP3)"])
    with col2:
        if "MP3" in tipo:
            qualidade = st.selectbox("Qualidade do Áudio:", ["Normal (192kbps)", "Alta (320kbps)"])
        else:
            qualidade = st.selectbox("Resolução Máxima:", ["1080p (Full HD)", "720p (HD)", "480p (SD)"])

    st.write("") 

    # BOTÃO 1: ANALISAR E MOSTRAR CAPA
    if st.button("ANALISAR LINK 🔍", use_container_width=True):
        if url:
            with st.spinner("🔍 Buscando informações, por favor aguarde..."):
                try:
                    st.session_state.info_video = obter_info_rapido(url)
                    st.session_state.bytes_arquivo = None
                    st.session_state.nome_arquivo = ""
                    st.session_state.fazer_scroll = True # Aciona o scroll
                    st.session_state.atirar_confete = False # Reseta o confete para o próximo vídeo
                except Exception as e:
                    st.error(f"Erro ao analisar: {e}")
        else:
            st.warning("Por favor, insira uma URL válida.")

st.markdown("---")

# EXIBIÇÃO DA CAPA E RESULTADOS
if st.session_state.info_video:
    info = st.session_state.info_video
    
    capa = extrair_capa(info)
    titulo = info.get("title", "Título Indisponível")
    uploader = info.get("uploader") or info.get("uploader_id") or "Desconhecido"
    
    card_html = f"""
    <div class="video-card">
        <div class="thumbnail-container">
            <img src="{capa}" class="thumbnail-img">
        </div>
        <div class="video-info-title">{titulo}</div>
        <div class="video-info-uploader">Canal: {uploader}</div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    st.write("") 

    if st.session_state.bytes_arquivo is None:
        if st.button(f"👉 BAIXAR AGORA - {tipo.upper()} 👈", use_container_width=True, type="primary"):
            with st.spinner("📦 Baixando e convertendo... Isso pode demorar para Playlists."):
                try:
                    info_full, pasta = processar_download(url, tipo, qualidade)
                    
                    if 'entries' in info_full:
                        final_path = "SkyDown_Playlist"
                        shutil.make_archive(final_path, 'zip', pasta)
                        final_file = final_path + ".zip"
                    else:
                        arquivos = [f for f in os.listdir(pasta)]
                        if arquivos:
                            final_file = os.path.join(pasta, arquivos[0])
                        else:
                            raise Exception("Arquivo não encontrado após download.")

                    with open(final_file, "rb") as f:
                        st.session_state.bytes_arquivo = f.read()
                        st.session_state.nome_arquivo = os.path.basename(final_file)
                    
                    if os.path.exists(pasta): shutil.rmtree(pasta)
                    
                    # SUCESSO! Avisa para atirar o confete na próxima tela
                    st.session_state.atirar_confete = True
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
    else:
        st.download_button(
            label=f"💾 SALVAR ARQUIVO - {st.session_state.nome_arquivo.upper()}",
            data=st.session_state.bytes_arquivo,
            file_name=st.session_state.nome_arquivo,
            mime="application/octet-stream",
            use_container_width=True
        )
        
        # --- ATIRA OS CONFETES QUANDO O BOTÃO APARECE ---
        if st.session_state.atirar_confete:
            carregar_js("script.js", "atirarConfete") # Chama a função de confete do script.js
            st.session_state.atirar_confete = False # Desliga para não repetir

    # --- FAZ O SCROLL AUTOMÁTICO QUANDO ANALISA A CAPA ---
    if st.session_state.fazer_scroll:
        carregar_js("script.js", "fazerScroll") # Chama a função de scroll do script.js
        st.session_state.fazer_scroll = False

# Slot de Anúncio Rodapé
#st.markdown('<div class="ad-slot">PUBLICIDADE</div>', unsafe_allow_html=True)

# Rodapé Customizado
st.markdown("<div class='custom-footer'>Desenvolvido por Alessandro © 2026</div>", unsafe_allow_html=True)
