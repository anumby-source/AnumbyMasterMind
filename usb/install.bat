rem pip download -r requirements.txt -d deps

rem installation de python
python-3.12.2-amd64.exe

set HERE="%~dp0"
set PATH=%HERE%\python\Scripts\;%HERE%\python\;%PATH%

rem test de la version de python
python.exe --version

rem installation des dépendances
python.exe -m pip install --no-warn-script-location --no-index --find-links=deps -r requirements.txt

rem utilisation de l'application
python.exe AnumbyMasterMind.py
