@echo off
setlocal ENABLEDELAYEDEXPANSION

:: === Config ===
set ZIP_NAME=project.zip
set TEMP_DIR=__deploy_temp__

:: === Exclude list (top-level folders/files to ignore) ===
set EXCLUDES=.git;.next;node_modules;.vscode;dist;.gitignore;README.md

:: === Cleanup old zip ===
if exist %ZIP_NAME% (
    echo Deleting old %ZIP_NAME%...
    del %ZIP_NAME%
)

:: === Remove old temp folder ===
if exist %TEMP_DIR% (
    echo Cleaning old temp folder...
    rmdir /S /Q %TEMP_DIR%
)

:: === Create temp folder ===
mkdir %TEMP_DIR%

:: === Copy top-level files ===
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

:: === Copy folders recursively ===
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

:: === Cleanup nested folders we want to exclude ===
echo Cleaning nested excludes inside %TEMP_DIR%...
for %%E in (%EXCLUDES%) do (
    for /d /r "%TEMP_DIR%" %%X in (%%E) do (
        echo Removing folder: %%X
        rmdir /S /Q "%%X"
    )
)

:: === Skip zipping for now ===
echo Skipping zip creation. Review copied files inside %TEMP_DIR%
pause
