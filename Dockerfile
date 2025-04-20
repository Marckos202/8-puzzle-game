FROM python:3.9-slim

# Instalar dependencias del sistema para tkinter y acceso web
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11-utils \
    novnc \
    x11vnc \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de requisitos y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Copiar y dar permisos al script para iniciar el servicio web
COPY start_web_service.sh .
RUN chmod +x start_web_service.sh

# Exponer el puerto para acceso web
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["./start_web_service.sh"]