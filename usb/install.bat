rem pip download -r requirements.txt -d deps

rem installation de python
python-3.12.2-amd64.exe

rem test de la version de python
py --version

rem installation des dépendances
py -m pip install --no-index --find-links=deps -r requirements.txt

rem utilisation de l'application
py AnumbyMasterMind.py
