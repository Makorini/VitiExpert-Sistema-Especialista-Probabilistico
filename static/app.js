// Interface geral: menu, idiomas, notícias e tema.


// Menu de navegação

const menuButton = document.getElementById("menu-button");

const navigation = document.getElementById("navigation");

menuButton?.addEventListener("click", () => {

    const isOpen = navigation.classList.toggle("open");

    menuButton.setAttribute(
        "aria-expanded",
        String(isOpen)
    );

});


// Seletor de idiomas

const languageToggle = document.getElementById("lang-toggle");

const languageMenu = document.getElementById("lang-menu");

languageToggle?.addEventListener("click", (event) => {

    // Impede que o clique seja propagado para o documento.
    event.stopPropagation();

    languageMenu.hidden = !languageMenu.hidden;

    languageToggle.setAttribute(
        "aria-expanded",
        String(!languageMenu.hidden)
    );

});


// Fecha o seletor quando o usuário clica fora dele.
document.addEventListener("click", (event) => {

    const isMenuOpen = languageMenu && !languageMenu.hidden;

    const clickedOutside = !event.target.closest(".lang-control");

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


for (const link of document.querySelectorAll(".lang-menu a")) {

    if (link.dataset.lang === window.VITI_LANG) {

        link.setAttribute("aria-current", "true");

    }

    // LINKS DE IDIOMA DEFINIDOS NO HTML.
    // O Flask já monta a URL da página atual para PT, EN e ES.
    // Não alteramos o endereço aqui, evitando reescritas indevidas.
    // A navegação e as traduções continuam sendo feitas pelo servidor.

}


// Notícias (foto da matéria ou ilustração)
const newsGrid = document.getElementById("news-grid");

if (newsGrid) {
    // Prefixo do site (ex.: /VitiExpert quando publicado em makorini.com.br/VitiExpert).
    const BASE = document.getElementById("viti-config")?.dataset.base || "";
    const fallbackImages = [1, 2, 3, 4, 5].map(number =>
        `${BASE}/static/news-fallback/vitiexpert-noticia-${number}.webp`
    );
    const lang = (document.documentElement.lang || "pt").toLowerCase();
    const illustrationText = lang.startsWith("en")
        ? "AI-generated illustration"
        : lang.startsWith("es")
            ? "Imagen ilustrativa generada por IA"
            : "Imagem ilustrativa gerada por IA";
    // Versão curta do aviso, usada no celular (a miniatura é pequena).
    const illustrationShort = lang.startsWith("en")
        ? "AI image"
        : lang.startsWith("es") ? "Generada por IA" : "Gerada por IA";

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
        label.title = illustrationText;
        const full = document.createElement("span");
        full.className = "news-label-full";
        full.textContent = illustrationText;
        const short = document.createElement("span");
        short.className = "news-label-short";
        short.textContent = illustrationShort;
        label.append(full, short);
        media.append(label);
        sequenceIllustrations();
    };

    const newsLang = ["pt", "en", "es"].includes(lang.slice(0, 2)) ? lang.slice(0, 2) : "pt";
    fetch(BASE + "/api/news?lang=" + newsLang, { signal: AbortSignal.timeout(30000) })
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
                    photo.src = BASE + item.image;
                } else {
                    useIllustration(article, photo, media);
                }
            }
            sequenceIllustrations();
        })
        .catch(showNewsError);
}


// Tema claro/escuro

const themeToggle = document.getElementById("theme-toggle");

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

updateThemeButton();

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


// Menu "Minha conta" no cabeçalho
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
