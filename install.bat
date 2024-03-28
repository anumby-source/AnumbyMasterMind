set /P VERSION=<VERSION
echo "version = %VERSION%"
set PACKAGE=AnumbyMasterMind
REM rmdir dist /s/q
REM python setup.py sdist bdist_wheel
REM twine check dist/%PACKAGE%-%VERSION%-py3-none-any.whl
REM tar tzf dist\%PACKAGE%-%VERSION%.tar.gz
set PASS=pypi-AgENdGVzdC5weXBpLm9yZwIkNzk4NjU0OWItNzFhNC00NGRjLTliY2ItNWNhNDRjOGQxM2VmAAIqWzMsIjI0NzM1Nzk0LTBiYjItNDFjNS1hNzE0LWI2ZDExMzQ5MDk0OSJdAAAGIOFTJkKGdYAQN519yfHKIxRdP9BU-9QhqZoj9zoYmq6t
REM twine upload -u __token__ -p %PASS% --repository-url https://test.pypi.org/legacy/ dist\%PACKAGE%-%VERSION%*.*
REM pip install -i https://test.pypi.org/simple/ AnumbyMasterMind==%VERSION%
twine upload -u __token__ -p %PASS% dist\%PACKAGE%-%VERSION%*.*
