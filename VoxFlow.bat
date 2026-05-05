@echo off
title VoxFlow — Voice to Text
cd /d "%~dp0"
python voxflow.py
if %errorlevel% neq 0 pause
