# Usar una imagen base de Python
FROM python:3.11

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get install -y wget unzip && \
    apt-get install -y libnss3 libgconf-2-4 libxi6 libgconf-2-4 libxss1 libxrandr2 && \
    apt-get install -y chromium

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de tu proyecto
COPY . .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Ejecutar tu script
CMD ["python", "main.py"]
