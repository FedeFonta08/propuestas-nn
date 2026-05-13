@echo off
title Lanzador de Campaña Masiva NN
cls
echo ==========================================================
echo   LANZADOR DE CAMPAÑA MASIVA NATIONALE-NEDERLANDEN
echo ==========================================================
echo.
echo ESTADO: Preparado para enviar a 965 contactos.
echo RECUERDA: Debes haber puesto tu contraseña de Google en:
echo d:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\enviar_campana_nn.py
echo.
echo El proceso enviará los correos con pausas de seguridad 
echo para evitar bloqueos. Tardará unos 45-60 minutos.
echo.
set /p choice="¿Deseas iniciar el envío REAL ahora? (S/N): "
if /i "%choice%"=="S" (
    echo.
    echo [!] Iniciando motor de envío...
    python d:\Users\ffont\Downloads\06_NATIONALE_NEDERLANDEN\enviar_campana_nn.py --send
) else (
    echo.
    echo [x] Envío cancelado por el usuario.
)
echo.
echo Proceso finalizado.
pause
