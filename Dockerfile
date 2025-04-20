FROM python:3.9-slim

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    xvfb \
    x11vnc \
    supervisor \
    python3-tk \
    libgl1-mesa-glx \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instalar noVNC directamente desde el repositorio
RUN mkdir -p /usr/share/novnc && \
    git clone https://github.com/novnc/noVNC.git /usr/share/novnc && \
    git clone https://github.com/novnc/websockify /usr/share/novnc/utils/websockify && \
    ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# Instalar dependencias de Python
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copiar archivos del proyecto
COPY . /app/

# Configurar supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto para noVNC
EXPOSE 8080

# Comando de inicio con supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
