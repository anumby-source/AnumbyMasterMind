set /P VERSION=<VERSION
echo "version = %VERSION%"
set PACKAGE=AnumbyMasterMind
set PASS=pypi-AgEIcHlwaS5vcmcCJDFkZjAxNzI4LTgxN2EtNGQxMi1hMDk2LTZmZGRkYzM3MzZkNAACKlszLCIyMDhmMTYxMi1lMTY1LTRiOWUtOTY2Zi1lNDY4YjIwYjIyODEiXQAABiC5A1EDkW8wCrtrjWvMq1c1_L_vAa53bVZ02CO_gm-UFQ
twine upload --verbose -u __token__ -p "%PASS%" dist\%PACKAGE%-%VERSION%*.*
