@REM Script para executar o script Python com ambiente virtual
@REM Se um ambiente virtual existe, ativa-o e executa o script Python
@REM Caso contrário, executa o script diretamente.

@echo off
cd /d "%~dp0"

@REM Define o caminho do ambiente virtual
set VENV_PATH=.venv\Scripts\activate.bat
@REM Define o comando a ser executado
set PYTHON_CMD=start "" python main.py %*
@REM set PYTHON_CMD=start "" pythonw main.py %*

@REM Verifica se existe um ambiente virtual Python na pasta atual
if exist "%VENV_PATH%" (
    echo Ativando ambiente virtual...
    call "%VENV_PATH%"
    %PYTHON_CMD%
    deactivate
) else (
    echo Nenhum ambiente virtual encontrado. Executando diretamente...
    %PYTHON_CMD%
)

@REM Verifica o código de saída do script Python
if %errorlevel% neq 0 (
    echo.
    echo Erro ao executar o script Python.
    echo Código de erro: %errorlevel%
    echo Verifique se o ambiente virtual está configurado corretamente e se todas as dependências estão instaladas.
    echo.
) else (
    echo Script executado com sucesso.
)
@REM NÃO Mantém o terminal aberto após a execução
@REM pause