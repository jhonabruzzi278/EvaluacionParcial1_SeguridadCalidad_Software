FROM node:22-alpine

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm ci --omit=dev

# Copiar código de la aplicación
COPY src/ ./src/
COPY sql/ ./sql/
COPY uploads/ ./uploads/

# Crear directorio para uploads y ceder todo al usuario sin privilegios
RUN mkdir -p uploads/contracts && chown -R node:node /app

# No ejecutar como root (CIS Docker 4.1, Trivy DS-0002)
USER node

# Exponer puerto
EXPOSE 4000

# Comando para iniciar la aplicación
CMD ["node", "src/app.js"]

