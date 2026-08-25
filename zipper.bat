@echo off
setlocal ENABLEDELAYEDEXPANSION

:: ==============================
:: Configuration
:: ==============================
set ZIP_NAME=project.zip
set TEMP_DIR=__deploy_temp__
set USE_RUNTIME_EXCLUDES=0

:: Top-level excludes
set EXCLUDES=.git .next node_modules .vscode dist .gitignore README.md

:: Docker bind-mounted runtime folders (relative paths)
set RUNTIME_EXCLUDES=backend\src\output backend\src\input backend\src\defines

:: ==============================
:: Cleanup old artifacts
:: ==============================
if exist "%ZIP_NAME%" (
    echo Deleting old %ZIP_NAME%...
    del "%ZIP_NAME%"
)

if exist "%TEMP_DIR%" (
    echo Cleaning old temp folder...
    rmdir /S /Q "%TEMP_DIR%"
)

mkdir "%TEMP_DIR%"

:: ==============================
:: Copy top-level files
:: ==============================
for /f "delims=" %%F in ('dir /b /a-d') do (
    set "SKIP=0"
    for %%E in (%EXCLUDES%) do (
        if /I "%%F"=="%%E" set "SKIP=1"
    )

    if !SKIP!==1 (
        echo Skipping file: %%F
    ) else (
        echo Copying file: %%F
        copy /Y "%%F" "%TEMP_DIR%\%%F" >nul
    )
)

:: ==============================
:: Copy folders recursively
:: ==============================
for /f "delims=" %%D in ('dir /b /ad') do (
    set "SKIP=0"
    for %%E in (%EXCLUDES%) do (
        if /I "%%D"=="%%E" set "SKIP=1"
    )

    if !SKIP!==1 (
        echo Skipping folder: %%D
    ) else (
        echo Copying folder: %%D
        xcopy /E /I /Y "%%D" "%TEMP_DIR%\%%D" >nul
    )
)

:: ==============================
:: Remove Docker runtime folders
:: ==============================
echo.
if "%USE_RUNTIME_EXCLUDES%"=="1" (
    echo Removing Docker runtime folders from deploy package...
    for %%R in (%RUNTIME_EXCLUDES%) do (
        if exist "%TEMP_DIR%\%%R" (
            echo Removing runtime folder: %%R
            rmdir /S /Q "%TEMP_DIR%\%%R"
        )
    )
) else (
    echo Skipping runtime excludes (USE_RUNTIME_EXCLUDES=0)
)


:: ==============================
:: Final verification
:: ==============================
echo.
echo =====================================
echo VERIFY: backend/src contents
echo =====================================
if exist "%TEMP_DIR%\backend\src" (
    dir "%TEMP_DIR%\backend\src"
) else (
    echo backend/src not found (unexpected)
)
echo =====================================

echo.
echo Deployment files prepared in %TEMP_DIR%
echo Review before zipping or uploading.
pause
