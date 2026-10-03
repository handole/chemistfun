# KimiFun (KimiFun)

**KimiFun** adalah platform pembelajaran kimia interaktif, virtual lab, dan evaluasi berbasis AI yang dirancang untuk guru dan siswa jenjang SMA (Kelas X, XI, XII).

Platform ini mendukung pengelolaan kurikulum terpusat per tingkatan kelas, laboratorium maya stoikiometri dan titrasi analitis, modul guided inquiry, serta asesmen kuis dengan analisis radar kompetensi sains.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (AsyncPG), Pydantic v2
- **Database**: [PostgreSQL 16](https://www.postgresql.org/) (Native `JSONB`, `UUID`, dan Enum)
- **Frontend**: [Vue.js 3](https://vuejs.org/) (Composition API), Vite, Tailwind CSS, Lucide Icons
- **AI Integration**: AI Tutor (Kimi), AI Lab Generator, AI Material Drafter via 9router gateway / Gemini API
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose

---

## 📁 Struktur Direktori

```text
KimiFun/
├── backend/                  # Source code API backend FastAPI
│   ├── app/
│   │   ├── core/             # Konfigurasi inti (database async engine, security, JWT)
│   │   ├── modules/          # Modul fungsionalitas (users, classes, content, assessment)
│   │   ├── services/         # Layanan AI (prompt_engine, ai_generator)
│   │   ├── utils/            # Dependencies auth/role guard & helpers
│   │   └── main.py           # Entrypoint aplikasi FastAPI
│   ├── Dockerfile            # Container build backend
│   └── requirements.txt      # Dependensi Python
├── frontend/                 # Single Page Application (Vue.js 3 + Vite)
│   ├── src/
│   │   ├── api/              # Client API wrapper
│   │   ├── components/       # Layout header, sidebar, chat widget (Kimi)
│   │   └── views/            # Dashboard guru, siswa, virtual lab, auth, kuis
│   ├── Dockerfile            # Container build frontend
│   └── package.json          # Dependensi Node.js & Vite
├── docs/                     # Dokumentasi arsitektur dan database
│   ├── README.md             # Indeks dokumentasi
│   └── database_schema.md    # Dokumentasi lengkap ERD & skema tabel PostgreSQL
├── docker-compose.yml        # Orkestrasi multi-kontainer (PostgreSQL, Backend, Frontend)
└── README.md                 # Dokumentasi utama proyek
```

---

## 🏛️ Arsitektur Hierarki Kelas & Modul

Aplikasi menerapkan model kurikulum berjenjang:

```text
Tingkatan Level (X, XI, XII)
  ├── Sub-Kelas (X-1, X-2, XI-IPA, dst.) -> Terhubung ke Siswa via Kode Enrollment
  └── Modul Kurikulum -> Materi Pembelajaran -> Virtual Lab & Kuis Asesmen
```

- **Guru**: Mengelola sub-kelas (kode enrollment), menyusun modul/materi per level tingkatan (`X`, `XI`, `XII`), mengonfigurasi parameter lab virtual, dan menerbitkan kuis evaluasi.
- **Siswa**: Bergabung ke sub-kelas menggunakan kode unik, otomatis mendapatkan akses ke seluruh modul kurikulum tingkatan level kelasnya, menjalankan simulasi titrasi lab interaktif, serta mengerjakan kuis dengan hasil penilaian radar kompetensi.

---

## 🚀 Panduan Menjalankan dengan Docker

### 1. Prasyarat
- [Docker Engine](https://docs.docker.com/engine/install/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### 2. Konfigurasi Environment
Salin template konfigurasi lokal:
```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

### 3. Build & Jalankan Kontainer
```bash
docker compose up -d --build
```

Perintah ini akan menyalakan 3 layanan:
1. `KimiFun_postgres` (Port 5432)
2. `KimiFun_backend` (Port 8000)
3. `KimiFun_frontend` (Port 5173, host `0.0.0.0`)

### 4. Akses Layanan

| Layanan | URL / Endpoint | Deskripsi |
| :--- | :--- | :--- |
| **Frontend Web App** | [http://localhost:5173/](http://localhost:5173/) | Aplikasi Web Vue 3 (Guru & Siswa) |
| **API Root** | [http://localhost:8000/](http://localhost:8000/) | Status backend |
| **API Health Check** | [http://localhost:8000/api/health](http://localhost:8000/api/health) | Endpoint health check backend & DB |
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Dokumentasi interaktif OpenAPI |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Dokumentasi alternatif OpenAPI |

> **Akses via Smartphone (Local Network)**:
> Frontend dijalankan dengan bind `0.0.0.0:5173`. Perangkat dalam satu jaringan Wi-Fi dapat mengakses melalui `http://<IP_KOMPUTER>:5173`.

---

## 🔧 Perintah Operasional

- **Melihat status layanan**:
  ```bash
  docker compose ps
  ```

- **Melihat log backend**:
  ```bash
  docker compose logs -f backend
  ```

- **Melihat log frontend**:
  ```bash
  docker compose logs -f frontend
  ```

- **Restart backend & frontend**:
  ```bash
  docker compose restart backend frontend
  ```

- **Masuk ke shell container backend**:
  ```bash
  docker compose exec backend bash
  ```

---

## 📚 Dokumentasi Terkait

- [Dokumentasi Skema Database & ERD](./docs/database_schema.md)
