
/**
 * ============================================================
 * VITIEXPERT — COMPORTAMENTO DA INTERFACE
 * ============================================================
 *
 * Projeto: Sistema Especialista Probabilístico para
 *          Diagnóstico de Doenças em Videiras
 *
 * Status: Em desenvolvimento e testagem
 *
 * Responsabilidades:
 * 1. Controlar o menu de navegação.
 * 2. Gerenciar o seletor de idiomas.
 * 3. Carregar notícias relacionadas à viticultura.
 * 4. Enviar os sintomas para a API Flask.
 * 5. Exibir os resultados do diagnóstico demonstrativo.
 *
 * IMPORTANTE:
 * Este arquivo não realiza cálculos probabilísticos.
 * O processamento das respostas acontece no servidor Flask.
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

    // Obtém o endereço da página atual.
    const url = new URL(window.location.href);

    // Atualiza o parâmetro do idioma na URL.
    url.searchParams.set("lang", link.dataset.lang);

    // Define o endereço correspondente ao idioma.
    link.href = url.pathname + url.search;

}


/* ============================================================
   3. NOTÍCIAS SOBRE UVAS E VITICULTURA
   ============================================================ */

// Localiza a área onde as notícias serão apresentadas.
const newsGrid = document.getElementById("news-grid");

// Executa a consulta somente se a área existir na página.
if (newsGrid) {

    // Consulta a API de notícias disponibilizada pelo Flask.
    fetch("/api/news", {
        signal: AbortSignal.timeout(8500)
    })

    // Verifica se a resposta HTTP foi bem-sucedida.
    .then((response) => {

        if (!response.ok) {
            throw new Error("News unavailable");
        }

        return response.json();

    })

    // Processa os dados recebidos da API.
    .then((data) => {

        // Remove o conteúdo anterior.
        newsGrid.replaceChildren();

        // Verifica se existem notícias disponíveis.
        if (!data.items?.length) {
            throw new Error("Empty news");
        }

        // Percorre cada notícia recebida.
        for (const item of data.items) {

            // Cria o link principal da notícia.
            const articleLink = document.createElement("a");

            articleLink.className = "news-card";
            articleLink.href = item.url;
            articleLink.target = "_blank";
            articleLink.rel = "noopener noreferrer";

            // Cria a identificação da fonte.
            const source = document.createElement("span");

            source.className = "news-meta";
            source.textContent = item.source || "Google Notícias";

            // Cria o título da notícia.
            const title = document.createElement("h3");

            title.textContent = item.title;

            // Cria o indicador visual de link externo.
            const arrow = document.createElement("span");

            arrow.className = "news-arrow";
            arrow.textContent = "↗";

            // Agrupa os elementos da notícia.
            articleLink.append(
                source,
                title,
                arrow
            );

            // Adiciona a notícia à página.
            newsGrid.append(articleLink);

        }

    })

    // Trata erros de conexão ou ausência de notícias.
    .catch(() => {

        // Limpa a área de notícias.
        newsGrid.replaceChildren();

        // Cria uma mensagem informativa.
        const message = document.createElement("p");

        message.className = "news-status";
        message.textContent = window.VITI_LABELS.news_unavailable;

        // Exibe a mensagem.
        newsGrid.append(message);

    });

}


/* ============================================================
   4. FORMULÁRIO DO SISTEMA ESPECIALISTA
   ============================================================ */

// Localiza o formulário de diagnóstico.
const diagnosisForm = document.getElementById("diagnose-form");

// Executa somente nas páginas que possuem o formulário.
if (diagnosisForm) {

    diagnosisForm.addEventListener("submit", async (event) => {

        // Impede o recarregamento automático da página.
        event.preventDefault();

        // Localiza a área destinada aos resultados.
        const resultsContainer = document.getElementById("results");

        // Exibe um indicador temporário de processamento.
        resultsContainer.textContent = "…";

        // Obtém os sintomas selecionados pelo usuário.
        const symptoms = [
            ...diagnosisForm.querySelectorAll("input:checked")
        ].map((input) => input.value);

        try {

            /* ------------------------------------------------
               4.1. ENVIO DOS SINTOMAS PARA O FLASK
               ------------------------------------------------ */

            // Envia as respostas para o endpoint de diagnóstico.
            const response = await fetch(
                "/api/diagnose?lang=" +
                encodeURIComponent(window.VITI_LANG),
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        symptoms: symptoms
                    })
                }
            );

            // Interrompe o processamento em caso de erro HTTP.
            if (!response.ok) {
                throw new Error("Request failed");
            }

            // Converte a resposta recebida para JSON.
            const data = await response.json();

            // Remove resultados anteriores.
            resultsContainer.replaceChildren();


            /* ------------------------------------------------
               4.2. TÍTULO DOS RESULTADOS
               ------------------------------------------------ */

            // Cria o título da seção.
            const heading = document.createElement("h2");

            heading.textContent = window.VITI_LABELS.result;

            // Insere o título na página.
            resultsContainer.append(heading);


            /* ------------------------------------------------
               4.3. TRATAMENTO DE RESULTADOS VAZIOS
               ------------------------------------------------ */

            // Verifica se nenhuma hipótese foi encontrada.
            if (!data.results.length) {

                const message = document.createElement("p");

                message.textContent =
                    data.message || window.VITI_LABELS.none;

                resultsContainer.append(message);

            }


            /* ------------------------------------------------
               4.4. EXIBIÇÃO DAS HIPÓTESES
               ------------------------------------------------ */

            // Percorre as hipóteses retornadas pelo servidor.
            for (const item of data.results) {

                // Cria o contêiner da hipótese.
                const resultItem = document.createElement("article");

                resultItem.className = "result-item";

                // Cria o cabeçalho do resultado.
                const resultHeader = document.createElement("div");

                resultHeader.className = "result-head";

                // Cria o nome da doença.
                const diseaseName = document.createElement("strong");

                diseaseName.textContent = item.name;

                // Cria o campo de pontuação demonstrativa.
                const score = document.createElement("span");

                score.textContent =
                    window.VITI_LABELS.score + ": " + item.score;

                // Agrupa o nome e a pontuação.
                resultHeader.append(
                    diseaseName,
                    score
                );

                // Cria o campo de justificativas.
                const evidence = document.createElement("p");

                evidence.textContent =
                    window.VITI_LABELS.reasons +
                    ": " +
                    item.evidence.join("; ");

                // Adiciona as informações ao resultado.
                resultItem.append(
                    resultHeader,
                    evidence
                );

                // Insere o resultado na página.
                resultsContainer.append(resultItem);

            }


            /* ------------------------------------------------
               4.5. AVISO SOBRE A VERSÃO DEMONSTRATIVA
               ------------------------------------------------ */

            // Cria o aviso de limitações do protótipo.
            const disclaimer = document.createElement("p");

            disclaimer.className = "notice";

            disclaimer.textContent =
                data.disclaimer ||
                window.VITI_LABELS.not_calibrated;

            // Exibe o aviso abaixo dos resultados.
            resultsContainer.append(disclaimer);

        } catch (error) {

            /* ------------------------------------------------
               4.6. TRATAMENTO DE ERROS
               ------------------------------------------------ */

            // Exibe uma mensagem quando a consulta falha.
            resultsContainer.textContent =
                "Não foi possível realizar a análise. / " +
                "Unable to assess symptoms.";

            // Registra o erro no console para depuração.
            console.error("Erro ao consultar o diagnóstico:", error);

        }

    });

}
