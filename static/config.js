/* Idioma e mensagens do VitiExpert para o JavaScript global. */
const vitiConfig = document.getElementById('viti-config');
if (vitiConfig) {
    window.VITI_LANG = vitiConfig.dataset.lang;
    window.VITI_LABELS = {news_unavailable: vitiConfig.dataset.newsUnavailable};
}
