@echo off
:: Set environment variable for the current script session
set SQL_FILE=%1
:: Enforce UTF-8 for Python
set PYTHONIOENCODING=utf-8
:: Activate the virtual environment (relative to this file's directory)
call "%~dp0demo_venv\Scripts\activate.bat"
:: Call bip_balance_client.py located in the same folder as this .bat file
python "%~dp0bip_balance_client.py" 