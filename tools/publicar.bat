@echo off
rem Migrometer ES - sube a GitHub el docs\data.json que deja la tarea diaria.
cd /d "%~dp0.."
echo ==== %date% %time% ====>> tools\publicar.log
git pull --rebase --autostash origin main >> tools\publicar.log 2>&1
git add docs
git diff --cached --quiet && (echo Sin cambios en los datos.>> tools\publicar.log & exit /b 0)
git commit -m "Datos actualizados %date%" >> tools\publicar.log 2>&1
git push origin main >> tools\publicar.log 2>&1
