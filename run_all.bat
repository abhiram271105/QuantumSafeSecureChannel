@echo off
setlocal
python check_environment.py
if errorlevel 1 goto :error
python test_ml_kem.py
if errorlevel 1 goto :error
python test_ml_dsa.py
if errorlevel 1 goto :error
python test_falcon.py
if errorlevel 1 goto :error
python main.py
if errorlevel 1 goto :error
python benchmark_crypto.py --iterations 20
if errorlevel 1 goto :error
echo.
echo All requested tests and benchmarks completed.
pause
exit /b 0
:error
echo.
echo A step failed. Read the error above and check README.md.
pause
exit /b 1
