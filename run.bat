@echo off
chcp 1251 > nul
cd /d "C:\Users\рс\Desktop\DataScience_Study\Simulative\11. Дипломный проект\marketplace_data_service-master\marketplace_data_service"
if not exist logs mkdir logs
call venv\Scripts\activate
python daily_update.py >> logs\update.log 2>&1