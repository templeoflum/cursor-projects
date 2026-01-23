@echo off
echo Starting AutoGen Studio...

:: Launch browser
start "" http://localhost:8081

:: Wait a moment for the browser to open
timeout /t 2

:: Start AutoGen Studio
autogenstudio ui 