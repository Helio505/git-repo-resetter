@REM Script to run the Python script using a virtual environment
@REM If a virtual environment exists, activates it and runs the Python script
@REM Otherwise, runs the script directly.

@echo off
cd /d "%~dp0"

@REM Defines the virtual environment path
set VENV_PATH=.venv\Scripts\activate.bat
@REM Defines the command to be executed
set PYTHON_CMD=start "" python main.py %*
@REM set PYTHON_CMD=start "" pythonw main.py %*

@REM Checks if a Python virtual environment exists in the current folder
if exist "%VENV_PATH%" (
    echo Activating virtual environment...
    call "%VENV_PATH%"
    %PYTHON_CMD%
    deactivate
) else (
    echo No virtual environment found. Running directly...
    %PYTHON_CMD%
)

@REM Checks the exit code of the Python script
if %errorlevel% neq 0 (
    echo.
    echo Error executing the Python script.
    echo Error code: %errorlevel%
    echo Please check if the virtual environment is properly configured and if all dependencies are installed.
    echo.
) else (
    echo Script executed successfully.
)
@REM Does NOT keep the terminal open after execution
@REM pause
