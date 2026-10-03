# Frontend KimiFun (Vue.js 3)

Folder ini disiapkan untuk aplikasi antarmuka pengguna (Frontend) KimiFun menggunakan **Vue.js 3**.

## Status
> **Belum Di-develop**: Bagian frontend belum dibuat.

## Rencana Setup & Dockerize Frontend

### 1. Inisialisasi Project (Rekomendasi)
Saat siap mengembangkan frontend, Anda dapat menginisialisasi project Vue 3 + Vite:
```bash
npm create vite@latest . -- --template vue
npm install
```

### 2. Contoh `frontend/Dockerfile` untuk Development
Buat file `frontend/Dockerfile`:
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

### 3. Aktivasi di `docker-compose.yml`
Setelah frontend dibuat dan memiliki `Dockerfile`, buka file `docker-compose.yml` di root project dan aktifkan (un-comment) blok service `frontend`:
```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  container_name: KimiFun_frontend
  restart: unless-stopped
  ports:
    - "5173:5173"
  volumes:
    - ./frontend:/app
    - /app/node_modules
  environment:
    - VITE_API_BASE_URL=http://localhost:8000
  depends_on:
    - backend
```
Lalu jalankan:
```bash
docker compose up -d --build
```
Aplikasi frontend akan dapat diakses di `http://localhost:5173`.

