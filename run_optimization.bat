@echo off
chcp 65001 > nul
echo ========================================================================
echo   株式ポートフォリオ最適化システム - 自動実行
echo ========================================================================
echo.

REM Pythonのパスを設定（環境に応じて変更してください）
set PYTHON_PATH=C:\python\313\python.exe

REM Pythonが見つからない場合はシステムのPythonを使用
if not exist "%PYTHON_PATH%" (
    echo 指定されたPythonが見つかりません: %PYTHON_PATH%
    echo システムのPythonを使用します...
    set PYTHON_PATH=python
)

echo Pythonパス: %PYTHON_PATH%
echo.

REM 自動実行スクリプトを実行
"%PYTHON_PATH%" "%~dp0run_optimization.py"

echo.
echo ========================================================================
pause

@REM Made with Bob
