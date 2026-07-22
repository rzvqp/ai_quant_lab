@echo off
rem Simulated `claude` executable used ONLY by scripts\tests\Test-AlphaAutomation.ps1.
rem Behavior is controlled entirely via environment variables set by the test harness
rem (FAKE_CLAUDE_EXIT_CODE, FAKE_CLAUDE_MARKER, FAKE_CLAUDE_TOUCH_STATE, FAKE_CLAUDE_STATE_FILE,
rem FAKE_CLAUDE_WIPE_STATE, FAKE_CLAUDE_SLEEP_MS, FAKE_CLAUDE_CALL_LOG). Never point production
rem config at this file.
powershell.exe -NoProfile -NoLogo -ExecutionPolicy Bypass -File "%~dp0fake_claude_impl.ps1" %*
exit /b %ERRORLEVEL%
