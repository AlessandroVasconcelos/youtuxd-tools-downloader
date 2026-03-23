// script.js

// CAIXINHA 1: Faz a tela descer
function fazerScroll() {
    setTimeout(function() {
        try {
            const doc = window.parent.document;
            const cards = doc.querySelectorAll('.video-card');
            if (cards.length > 0) {
                cards[cards.length - 1].scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        } catch(e) {
            console.log("Erro no scroll:", e);
        }
    }, 600);
}

// CAIXINHA 2: Atira os confetes (LATERAIS + CENTRO)
function atirarConfete() {
    try {
        const parentDoc = window.parent.document;
        const parentWin = window.parent;

        // Função que dispara os TRÊS canhões simultaneamente
        function soltarFesta() {
            // 1. Canhão da ESQUERDA (x: 0)
            parentWin.confetti({
                particleCount: 100,
                angle: 60,             // Diagonal para a direita
                spread: 80,
                origin: { x: 0, y: 0.8 },
                colors: ['#FF0000', '#00f2ff', '#ffffff'],
                scalar: 2.5
            });

            // 2. Canhão da DIREITA (x: 1)
            parentWin.confetti({
                particleCount: 100,
                angle: 120,            // Diagonal para a esquerda
                spread: 80,
                origin: { x: 1, y: 0.8 },
                colors: ['#FF0000', '#00f2ff', '#ffffff'],
                scalar: 2.5
            });

            // 3. Canhão do CENTRO (x: 0.5)
            parentWin.confetti({
                particleCount: 150,
                angle: 90,             // Reto para cima
                spread: 100,           // Espalha bem no meio
                origin: { x: 0.5, y: 0.8 },
                colors: ['#FF0000', '#00f2ff', '#ffffff'],
                scalar: 2.5
            });
        }

        // Verifica se a biblioteca já está carregada
        if (parentWin.confetti) {
            soltarFesta();
            return;
        }

        // Instala a biblioteca se for a primeira vez
        var script = parentDoc.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js';
        
        script.onload = function() {
            soltarFesta();
        };
        parentDoc.head.appendChild(script);

    } catch(e) {
        console.log("Erro no confete:", e);
    }
}
