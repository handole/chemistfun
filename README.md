# ChemistFun

**ChemistFun** adalah platform pembelajaran kimia interaktif dan laboratorium virtual (Virtual Lab) berbasis kecerdasan buatan (AI) yang dirancang untuk membantu guru dan siswa dalam simulasi eksperimen kimia dan evaluasi pemahaman konsep secara komprehensif.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), Celery
- **Database**: [PostgreSQL 16](https://www.postgresql.org/) (Didukung native `JSONB` & `UUID`)
- **Frontend** *(Dalam Rencana)*: [Vue.js 3](https://vuejs.org/) + Vite + Tailwind CSS
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose

---

## 📁 Struktur Direktori

```text
chemistfun/
├── backend/                  # Source code API backend FastAPI
│   ├── app/
│   │   ├── core/             # Konfigurasi inti (database, security, celery)
│   │   ├── modules/          # Modul fungsionalitas (users, classes, content, assessment)
│   │   ├── services/         # Layanan eksternal (AI generator, prompt engine)
│   │   ├── utils/            # Helper, dependencies, dan custom exceptions
│   │   └── main.py           # Entrypoint aplikasi FastAPI
│   ├── Dockerfile            # Multi-stage/development Dockerfile untuk backend
│   ├── requirements.txt      # Dependensi Python backend
│   └── .dockerignore         # Filter file konteks build backend
├── frontend/                 # Workspace frontend (Vue.js 3 - placeholder)
│   └── README.md             # Panduan inisiasi & integrasi frontend ke Docker
├── docs/                     # Dokumentasi arsitektur dan database
│   ├── README.md             # Indeks dokumentasi
│   └── database_schema.md    # Dokumentasi lengkap ERD & skema tabel SQLAlchemy
├── .dockerignore             # Filter file konteks Docker root
├── .env.example              # Template variabel lingkungan
├── docker-compose.yml        # Orkestrasi kontainer (PostgreSQL, Backend, Frontend)
└── README.md                 # Dokumentasi utama proyek
```

---

## 🚀 Panduan Menjalankan dengan Docker

### 1. Prasyarat
Pastikan Anda telah menginstal:
- [Docker Engine](https://docs.docker.com/engine/install/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### 2. Salin Konfigurasi Environment
Buat file `.env` dari template yang telah disediakan:
```bash
cp .env.example .env
```
Anda dapat menyesuaikan kredensial database dan port jika diperlukan pada file `.env`.

### 3. Build & Jalankan Kontainer
Jalankan perintah berikut pada root direktori:
```bash
docker compose up -d --build
```
Perintah ini akan:
1. Menjalankan kontainer **PostgreSQL 16** dan memastikan database siap (`service_healthy`).
2. Melakukan build image **FastAPI Backend** dan menjalankannya dengan fitur *live-reload*.
3. Menginisialisasi tabel-tabel database secara otomatis saat backend pertama kali aktif.

### 4. Verifikasi Layanan
Setelah kontainer berjalan, layanan dapat diakses melalui:

| Layanan | URL / Endpoint | Deskripsi |
| :--- | :--- | :--- |
| **API Root** | [http://localhost:8000/](http://localhost:8000/) | Status server backend |
| **API Health Check** | [http://localhost:8000/api/health](http://localhost:8000/api/health) | Endpoint cek status operasional |
| **Swagger UI (Interactive)** | [http://localhost:8000/docs](http://localhost:8000/docs) | Dokumentasi interaktif OpenAPI |
| **ReDoc UI** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Dokumentasi alternatif OpenAPI |
| **PostgreSQL** | `localhost:5432` | Port database PostgreSQL |

---

## 📦 Rincian Layanan Docker Compose

### 1. `postgres` (Database)
- Menggunakan base image `postgres:16-alpine`.
- Persistensi data tersimpan secara aman menggunakan volume Docker bernama `postgres_data`.
- Dilengkapi mekanisme `healthcheck` menggunakan `pg_isready` untuk memastikan koneksi siap sebelum backend dijalankan.

### 2. `backend` (FastAPI)
- Dibangun dari `backend/Dockerfile` berbasis `python:3.10-slim`.
- Folder `./backend` di-*mount* ke dalam kontainer `/app` sehingga perubahan kode (*hot-reload*) langsung aktif tanpa perlu rebuild kontainer.
- Terhubung otomatis ke layanan PostgreSQL melalui Docker Network internal `chemistfun_network`.

### 3. `frontend` (Vue.js 3 - Placeholder)
- **Status**: Saat ini belum di-develop.
- Konfigurasi service telah disiapkan di dalam [docker-compose.yml](file:///Users/handokodenih/DEV/chemistfun/docker-compose.yml) dalam bentuk komentar.
- Panduan lengkap inisialisasi dan pengaktifan frontend ke dalam Docker dapat dibaca di [frontend/README.md](file:///Users/handokodenih/DEV/chemistfun/frontend/README.md).

---

## 🔧 Perintah Docker yang Sering Digunakan

- **Melihat status kontainer yang sedang berjalan**:
  ```bash
  docker compose ps
  ```

- **Melihat log backend secara realtime**:
  ```bash
  docker compose logs -f backend
  ```

- **Melihat seluruh log kontainer**:
  ```bash
  docker compose logs -f
  ```

- **Mengakses shell terminal di dalam kontainer backend**:
  ```bash
  docker compose exec backend bash
  ```

- **Mengakses terminal database PostgreSQL (psql)**:
  ```bash
  docker compose exec postgres psql -U postgres -d chemistfun_db
  ```

- **Restart layanan tertentu (misal: backend)**:
  ```bash
  docker compose restart backend
  ```

- **Menghentikan seluruh layanan**:
  ```bash
  docker compose down
  ```

- **Menghentikan seluruh layanan beserta menghapus volume data (Reset Database)**:
  ```bash
  docker compose down -v
  ```

---

## 📖 Dokumentasi Lanjutan

- **[Dokumentasi Skema Basis Data & Model ERD](docs/database_schema.md)**: Diagram relasi ERD lengkap, spesifikasi tabel, tipe data native PostgreSQL (JSONB, UUID, ENUM), dan pemetaan model SQLAlchemy 2.0.
- **[Panduan Inisiasi Frontend](frontend/README.md)**: Petunjuk inisialisasi Vue.js 3, pembuatan Dockerfile frontend, dan aktivasi service pada Docker Compose.

