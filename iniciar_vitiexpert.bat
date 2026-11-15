@echo off
chcp 65001 >nul
title VitiExpert
rem ============================================================
rem  VitiExpert - inicia o sistema com dois cliques (Windows).
rem  1a vez: cria o ambiente .venv e instala as bibliotecas
rem  (precisa de internet). Depois abre o site no navegador.
rem  Para encerrar: feche esta janela ou aperte Ctrl+C.
rem ============================================================
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo.
    echo  [ERRO] Python nao encontrado neste computador.
    echo  Instale o Python 3.11 ou mais novo em https://www.python.org/downloads/
    echo  e marque a opcao "Add python.exe to PATH" na instalacao.
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo  Preparando o VitiExpert pela primeira vez...
    %PY% -m venv .venv || goto erro
)

echo  Conferindo as bibliotecas...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt || goto erro

if not exist ".env" (
    echo.
    echo  [AVISO] Arquivo .env nao encontrado: o codigo de confirmacao de cadastro
    echo  aparecera nesta janela em vez de ser enviado por e-mail.
)

echo.
echo  VitiExpert rodando em http://127.0.0.1:5000
echo  Para encerrar, feche esta janela.
echo.
rem Abre o navegador alguns segundos depois, quando o servidor ja estiver no ar.
start "" cmd /c "timeout /t 3 /nobreak >nul & start http://127.0.0.1:5000"
".venv\Scripts\python.exe" app.py
pause
exit /b 0

:erro
echo.
echo  [ERRO] Nao foi possivel preparar o VitiExpert. Verifique a internet
echo  (necessaria na primeira vez) e tente novamente.
pause
exit /b 1
