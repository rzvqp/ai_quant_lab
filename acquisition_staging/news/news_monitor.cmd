@echo off
REM Permanent ForexFactory news monitor (Task Scheduler entry point).
REM Recurring model: Task Scheduler fires this every 5 min and runs ONE cycle (--once). The monitor
REM is stateless between cycles (all state on disk), so a recurring one-shot is equivalent to a loop
REM and strictly more crash-robust (Scheduler owns the cadence; a cycle crash needs no restart logic).
REM MultipleInstances=IgnoreNew prevents overlap if a cycle runs long.
setlocal
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set PY="C:\Users\MEDION GAMING\AppData\Local\Python\pythoncore-3.14-64\python.exe"
set SCRIPT="C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\news\news_monitor.py"
set LOG="C:\Users\MEDION GAMING\ai_quant_lab-data-acq\acquisition_staging\news\news_monitor.log"
echo ==== run %DATE% %TIME% ==== >> %LOG%
%PY% %SCRIPT% --once >> %LOG% 2>&1
echo ==== exit=%ERRORLEVEL% %DATE% %TIME% ==== >> %LOG%
endlocal
