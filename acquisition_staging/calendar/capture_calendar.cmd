@echo off
REM Weekly ForexFactory calendar capture wrapper (Windows Task Scheduler entry point).
REM as-of freezing, append-only, best-effort git push + weekly notification.
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PY="C:\Users\MEDION GAMING\AppData\Local\Python\pythoncore-3.14-64\python.exe"
set SCRIPT="C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\calendar\capture_calendar.py"
set LOG="C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\calendar\capture_runs.log"
echo ==== %DATE% %TIME% ==== >> %LOG%
%PY% %SCRIPT% >> %LOG% 2>&1
echo exit=%ERRORLEVEL% >> %LOG%
endlocal
