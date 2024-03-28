set /P VERSION=<VERSION
echo "version = %VERSION%"
set PACKAGE=AnumbyMasterMind
set PASS=pypi-AgEIcHlwaS5vcmcCJDQ4YWNjNzIwLTIyYTgtNDAwYi1hNDY2LTQ0NjhmZGNkNTBiNQACKlszLCIyMDhmMTYxMi1lMTY1LTRiOWUtOTY2Zi1lNDY4YjIwYjIyODEiXQAABiBtv16xjrxHSd6Wxlg-xIe5qgntUuFCk-ViEIlbpilqDg
twine upload -u __token__ -p %PASS% dist\%PACKAGE%-%VERSION%*.*
