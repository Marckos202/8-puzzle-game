#!/bin/bash

# Instalar noVNC si no está instalado
apt-get update
apt-get install -y novnc x11vnc

# Iniciar Xvfb (servidor X virtual)
Xvfb :1 -screen 0 1024x768x16 &
export DISPLAY=:1

# Iniciar VNC server
x11vnc -display :1 -nopw -forever -xkb &

# Iniciar noVNC (interface web para VNC)
/usr/share/novnc/utils/launch.sh --vnc localhost:5900 --listen 8080 &

# Iniciar la aplicación Python
python /app/main.py