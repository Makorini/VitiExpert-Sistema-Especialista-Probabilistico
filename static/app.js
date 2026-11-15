
/**
 * ============================================================
 * VITIEXPERT — COMPORTAMENTO DA INTERFACE
 * ============================================================
 *
 * Projeto: Sistema Especialista Probabilístico para
 *          Diagnóstico de Doenças em Videiras
 *
 * Responsabilidades:
 * 1. Controlar o menu de navegação.
 * 2. Gerenciar o seletor de idiomas.
 * 3. Carregar notícias relacionadas à viticultura.
 * 4. Alternar o tema claro e escuro.
 *
 * ============================================================
 */


/* ============================================================
   1. MENU DE NAVEGAÇÃO
   ============================================================ */

// Localiza o botão responsável pelo menu.
const menuButton = document.getElementById("menu-button");

// Localiza o elemento de navegação.
const navigation = document.getElementById("navigation");

// Adiciona o evento de clique ao botão, caso ele exista.
menuButton?.addEventListener("click", () => {

    // Alterna a classe responsável por abrir ou fechar o menu.
    const isOpen = navigation.classList.toggle("open");

    // Atualiza o estado de acessibilidade do botão.
    menuButton.setAttribute(
        "aria-expanded",
        String(isOpen)
    );

});


/* ============================================================
   2. SELETOR DE IDIOMAS
   ============================================================ */

// Localiza o botão que abre a seleção de idiomas.
const languageToggle = document.getElementById("lang-toggle");

// Localiza o menu que contém os idiomas disponíveis.
const languageMenu = document.getElementById("lang-menu");

// Controla a abertura e o fechamento do seletor.
languageToggle?.addEventListener("click", (event) => {

    // Impede que o clique seja propagado para o documento.
    event.stopPropagation();

    // Alterna a visibilidade do menu.
    languageMenu.hidden = !languageMenu.hidden;

    // Atualiza o atributo de acessibilidade.
    languageToggle.setAttribute(
        "aria-expanded",
        String(!languageMenu.hidden)
    );

});


// Fecha o seletor quando o usuário clica fora dele.
document.addEventListener("click", (event) => {

    // Verifica se o menu está aberto.
    const isMenuOpen = languageMenu && !languageMenu.hidden;

    // Verifica se o clique ocorreu fora do seletor.
    const clickedOutside = !event.target.closest(".lang-control");

    // Fecha o menu quando as duas condições são verdadeiras.
    if (isMenuOpen && clickedOutside) {

        languageMenu.hidden = true;

        languageToggle?.setAttribute(
            "aria-expanded",
            "false"
        );

    }

});


// Permite fechar o seletor pressionando Escape.
document.addEventListener("keydown", (event) => {

    if (event.key === "Escape" && languageMenu) {

        languageMenu.hidden = true;

        languageToggle?.setAttribute(
            "aria-expanded",
            "false"
        );

    }

});


// Configura os links dos idiomas disponíveis.
for (const link of document.querySelectorAll(".lang-menu a")) {

    // Destaca o idioma atualmente selecionado.
    if (link.dataset.lang === window.VITI_LANG) {

        link.setAttribute("aria-current", "true");

    }

    // LINKS DE IDIOMA DEFINIDOS NO HTML.
    // O Flask já monta a URL da página atual para PT, EN e ES.
    // Não alteramos o endereço aqui, evitando reescritas indevidas.
    // A navegação e as traduções continuam sendo feitas pelo servidor.

}


/* ============================================================
   3. NOTÍCIAS DA VITICULTURA — FOTOS REAIS OU ILUSTRAÇÕES
   ============================================================ */
const newsGrid = document.getElementById("news-grid");

if (newsGrid) {
    const fallbackImages = [1, 2, 3, 4, 5].map(number =>
        `/static/news-fallback/vitiexpert-noticia-${number}.webp`
    );
    const lang = (document.documentElement.lang || "pt").toLowerCase();
    const illustrationText = lang.startsWith("en")
        ? "AI-generated illustration"
        : lang.startsWith("es")
            ? "Imagen ilustrativa generada por IA"
            : "Imagem ilustrativa gerada por IA";

    const showNewsError = () => {
        newsGrid.replaceChildren();
        const message = document.createElement("p");
        message.className = "news-status";
        message.textContent = window.VITI_LABELS.news_unavailable;
        newsGrid.append(message);
    };

    // Mantém uma ordem estável na tela: 1, 2, 3, 4, 5, depois recomeça.
    // Quando uma foto real falha, ela entra na sequência, mesmo que as
    // imagens externas terminem de carregar em momentos diferentes.
    const sequenceIllustrations = () => {
        const cards = Array.from(newsGrid.querySelectorAll(
            '.news-card[data-illustrative="true"]'
        ));
        cards.forEach((card, index) => {
            const image = card.querySelector(".news-photo-img");
            if (!image || card.dataset.fallbackBroken === "true") return;
            const src = fallbackImages[index % fallbackImages.length];
            if (image.getAttribute("src") !== src) image.src = src;
        });
    };

    const useIllustration = (article, photo, media) => {
        if (article.dataset.illustrative === "true") return;
        article.dataset.illustrative = "true";
        // Ilustrações são locais e leves: carregam já, sem esperar a rolagem.
        photo.loading = "eager";
        photo.alt = illustrationText;
        const label = document.createElement("span");
        label.className = "news-illustrative-label";
        label.textContent = illustrationText;
        media.append(label);
        sequenceIllustrations();
    };

    const newsLang = ["pt", "en", "es"].includes(lang.slice(0, 2)) ? lang.slice(0, 2) : "pt";
    fetch("/api/news?lang=" + newsLang, { signal: AbortSignal.timeout(30000) })
        .then(response => {
            if (!response.ok) throw new Error("News unavailable");
            return response.json();
        })
        .then(data => {
            const items = (data.items || []).filter(item =>
                item && typeof item.title === "string" && typeof item.url === "string"
                && item.url.startsWith("https://")
            );
            if (!items.length) throw new Error("No recent viticulture news");
            newsGrid.replaceChildren();

            for (const item of items) {
                const article = document.createElement("a");
                article.className = "news-card";
                article.href = item.url;
                article.target = "_blank";
                article.rel = "noopener noreferrer";

                const media = document.createElement("div");
                media.className = "news-photo";
                const photo = document.createElement("img");
                photo.className = "news-photo-img";
                photo.alt = ""; // Título ao lado identifica a publicação.
                photo.loading = "lazy";
                photo.decoding = "async";
                let attemptedOriginal = false;
                let fallbackFailures = 0;
                photo.addEventListener("error", () => {
                    if (article.dataset.illustrative === "true") {
                        // Um erro atrasado da foto original (já substituída)
                        // não pode apagar a ilustração: só conta o erro da
                        // própria ilustração local.
                        const failed = photo.getAttribute("src") || "";
                        if (!failed.includes("/news-fallback/")) return;
                        fallbackFailures += 1;
                        if (fallbackFailures < fallbackImages.length) {
                            // Tenta a próxima ilustração da sequência.
                            const next = fallbackImages[
                                (fallbackImages.indexOf(failed) + 1) % fallbackImages.length
                            ];
                            photo.src = next;
                            return;
                        }
                        // Nenhuma ilustração carregou: a notícia continua
                        // na página sem uma imagem quebrada.
                        article.dataset.fallbackBroken = "true";
                        photo.remove();
                        return;
                    }
                    // Prioridade: URL da fotografia na própria publicação.
                    if (!attemptedOriginal && typeof item.image_original === "string"
                            && item.image_original.startsWith("https://")) {
                        attemptedOriginal = true;
                        photo.src = item.image_original;
                        return;
                    }
                    useIllustration(article, photo, media);
                });
                media.append(photo);

                const content = document.createElement("div");
                content.className = "news-content";
                const meta = document.createElement("div");
                meta.className = "news-meta";
                const source = document.createElement("span");
                source.textContent = item.source || "Fonte externa";
                meta.append(source);
                if (item.published && !Number.isNaN(Date.parse(item.published))) {
                    const date = document.createElement("time");
                    date.dateTime = new Date(item.published).toISOString();
                    date.textContent = new Intl.DateTimeFormat(
                        document.documentElement.lang || "pt-BR",
                        { day: "2-digit", month: "short", year: "numeric" }
                    ).format(new Date(item.published));
                    meta.append(date);
                }

                const title = document.createElement("h3");
                title.textContent = item.title;
                if (item.translated && typeof item.title_original === "string") {
                    // Mostra o título original em português ao passar o mouse.
                    title.title = item.title_original;
                    title.lang = newsLang;
                }
                content.append(meta, title);

                if (item.description) {
                    const excerpt = document.createElement("p");
                    excerpt.className = "news-excerpt";
                    excerpt.textContent = item.description;
                    content.append(excerpt);
                }
                article.append(media, content);
                newsGrid.append(article);

                if (typeof item.image === "string"
                    && item.image.startsWith("/api/news/photo/")) {
                    photo.src = item.image;
                } else {
                    useIllustration(article, photo, media);
                }
            }
            sequenceIllustrations();
        })
        .catch(showNewsError);
}


/* ============================================================
   4. TEMA CLARO E ESCURO
   ============================================================ */

const themeToggle = document.getElementById("theme-toggle");

// Atualiza o texto acessível para indicar a próxima ação.
function updateThemeButton() {
    if (!themeToggle) return;

    const isLight = document.documentElement.dataset.theme === "light";

    themeToggle.setAttribute("aria-pressed", String(isLight));
    const chosenLang = (document.documentElement.lang || "pt").slice(0, 2);
    const themeStrings = {
        pt: ["Ativar modo escuro", "Ativar modo claro"],
        en: ["Switch to dark mode", "Switch to light mode"],
        es: ["Activar modo oscuro", "Activar modo claro"]
    };
    const labels = themeStrings[chosenLang] || themeStrings.pt;

    themeToggle.setAttribute(
        "aria-label",
        isLight ? labels[0] : labels[1]
    );
    themeToggle.title = isLight ? labels[0] : labels[1];
}

// Sincroniza o botão com o tema carregado no início da página.
updateThemeButton();

// Alterna exclusivamente as cores, sem alterar os dados do sistema.
themeToggle?.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "light"
        ? "dark"
        : "light";

    document.documentElement.dataset.theme = nextTheme;

    try {
        localStorage.setItem("vitiexpert-theme", nextTheme);
    } catch (error) {
        // Navegadores com armazenamento bloqueado usam o tema da sessão.
    }

    updateThemeButton();
});


/* ============================================================
   5. MENU "MINHA CONTA" NO CABEÇALHO
   ============================================================ */
const accountToggle = document.getElementById("account-toggle");
const accountMenu = document.getElementById("account-menu");

const closeAccountMenu = () => {
    if (!accountMenu || accountMenu.hidden) return;
    accountMenu.hidden = true;
    accountToggle?.setAttribute("aria-expanded", "false");
};

accountToggle?.addEventListener("click", (event) => {
    event.stopPropagation();
    accountMenu.hidden = !accountMenu.hidden;
    accountToggle.setAttribute("aria-expanded", String(!accountMenu.hidden));
});
document.addEventListener("click", (event) => {
    if (!event.target.closest(".account-control")) closeAccountMenu();
});
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeAccountMenu();
});


/* ============================================================
   6. CONFIRMAÇÃO ANTES DE SAIR OU EXCLUIR
   Todo formulário com data-confirm pergunta antes de enviar.
   ============================================================ */
const confirmDialog = document.getElementById("viti-confirm");

document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
        if (form.dataset.confirmed === "true") return;
        event.preventDefault();
        const message = form.dataset.confirm;
        // Sem suporte a <dialog>: usa a confirmação do navegador.
        if (!confirmDialog || typeof confirmDialog.showModal !== "function") {
            if (window.confirm(message)) { form.dataset.confirmed = "true"; form.requestSubmit(); }
            return;
        }
        confirmDialog.querySelector("#viti-confirm-text").textContent = message;
        const yes = confirmDialog.querySelector(".viti-confirm-yes");
        const no = confirmDialog.querySelector(".viti-confirm-no");
        yes.textContent = form.dataset.confirmYes || yes.textContent;
        yes.classList.toggle("is-danger", form.hasAttribute("data-confirm-danger"));
        const finish = (accepted) => {
            confirmDialog.close();
            yes.onclick = no.onclick = null;
            if (accepted) { form.dataset.confirmed = "true"; form.requestSubmit(); }
        };
        yes.onclick = () => finish(true);
        no.onclick = () => finish(false);
        confirmDialog.oncancel = () => { yes.onclick = no.onclick = null; };
        closeAccountMenu();
        confirmDialog.showModal();
        no.focus(); // o foco começa em "Cancelar", para evitar confirmar sem querer
    });
});
