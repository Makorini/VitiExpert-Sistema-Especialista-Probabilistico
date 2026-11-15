/**
 * VitiExpert — envio de e-mail pelo Google Apps Script (mesmo método do projeto do salão).
 *
 * Este código roda DENTRO da conta Google makorini.dev@gmail.com e envia com
 * MailApp.sendEmail, sem senha de app. O VitiExpert (Python) chama este script
 * pela internet e manda: destinatário, assunto e mensagem.
 *
 * COMO INSTALAR (uma vez só) — ver também README.md, seção "Envio de e-mail":
 *  1. Entre em https://script.google.com com a conta makorini.dev@gmail.com
 *     e crie um "Novo projeto". Cole TODO este arquivo no lugar do código.
 *  2. Em "Configurações do projeto" (engrenagem) > "Propriedades do script",
 *     adicione a propriedade  VITIEXPERT_TOKEN  com um texto secreto qualquer
 *     (ex.: uma frase longa). O mesmo texto vai no .env do VitiExpert.
 *  3. Rode a função  autorizarEnvioEmail  uma vez (botão "Executar") e aceite
 *     as permissões — igual ao projeto do salão.
 *  4. "Implantar" > "Nova implantação" > tipo "App da Web":
 *        Executar como:  Eu (makorini.dev@gmail.com)
 *        Quem pode acessar:  Qualquer pessoa
 *     Copie a URL que termina em /exec e coloque no .env do VitiExpert.
 */

const NOME_REMETENTE = 'VitiExpert';
const EMAIL_RESPOSTA = 'makorini.dev@gmail.com';

function doPost(e) {
  try {
    const dados = JSON.parse((e && e.postData && e.postData.contents) || '{}');
    const token = PropertiesService.getScriptProperties().getProperty('VITIEXPERT_TOKEN');
    if (!token || dados.token !== token) {
      return resposta_({ ok: false, erro: 'token inválido' });
    }
    if (!dados.para || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(dados.para)) {
      return resposta_({ ok: false, erro: 'destinatário inválido' });
    }
    MailApp.sendEmail({
      to: dados.para,
      subject: String(dados.assunto || 'VitiExpert').slice(0, 200),
      body: String(dados.texto || ''),
      htmlBody: dados.html ? String(dados.html) : undefined,
      name: String(dados.nome || NOME_REMETENTE).slice(0, 80),
      replyTo: EMAIL_RESPOSTA
    });
    return resposta_({ ok: true });
  } catch (erro) {
    return resposta_({ ok: false, erro: String(erro) });
  }
}

function doGet() {
  return resposta_({ ok: true, servico: 'VitiExpert e-mail' });
}

/** Rode uma vez para o Google pedir a permissão de enviar e-mails. */
function autorizarEnvioEmail() {
  MailApp.sendEmail({
    to: EMAIL_RESPOSTA,
    subject: 'Autorização de envio - VitiExpert',
    body: 'Autorização do envio de e-mails do VitiExpert concluída.'
  });
  return 'E-mail de autorização enviado para ' + EMAIL_RESPOSTA + '.';
}

function resposta_(objeto) {
  return ContentService.createTextOutput(JSON.stringify(objeto))
    .setMimeType(ContentService.MimeType.JSON);
}
