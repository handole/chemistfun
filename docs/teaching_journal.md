# Fitur Jurnal Mengajar & Presensi Siswa (Teaching Journal Management)

Dokumen ini menjelaskan arsitektur, skema data, endpoint API, dan alur antarmuka pengguna untuk fitur **Jurnal Mengajar Guru**, pencatatan presensi siswa, checklist ketercapaian silabus materi, serta penilaian tugas harian siswa pada platform **KimiFun**.

---

## 1. Ikhtisar Fitur (Feature Overview)

Fitur Jurnal Mengajar dirancang untuk mempermudah guru dalam:
1. **Administrasi Pembelajaran**: Merekam tanggal, waktu sesi (jam mulai dan selesai), kelas tujuan, dan topik/judul pertemuan pembelajaran kimia.
2. **Ketercapaian Materi (Syllabus Tracking)**: Memilih materi modul yang direncanakan (*target/planned*) dan menandai materi yang tuntas dibahas (*completed/checked*) secara interaktif.
3. **Presensi Siswa**: Mengelola status kehadiran seluruh siswa di kelas terkait (`present` / Hadir, `sick` / Sakit, `permitted` / Izin, `absent` / Alpa) dengan fitur tombol cepat *"Set Semua"*.
4. **Penilaian Tugas Siswa (Assignment Scoring)**: Menginput nilai tugas siswa (0 - 100) per pertemuan yang otomatis dihitung rata-ratanya pada kartu ringkasan jurnal.
5. **Refleksi Guru**: Menulis catatan evaluasi kendala pemahaman konsep atau catatan praktikum kimia untuk pertemuan lanjutan.

---

## 2. Struktur Data & Model Relasional

Modul backend berlokasi di `backend/app/modules/journals/`.

### 2.1. Enum Status Kehadiran (`attendance_status`)
- `present`: Siswa hadir di kelas / lab.
- `sick`: Siswa berhalangan sakit.
- `permitted`: Siswa izin dengan keterangan.
- `absent`: Siswa tanpa keterangan / alpa.

### 2.2. Relasi Tabel
- `users` (Teacher) `1 : N` `teaching_journals`
- `classes` `1 : N` `teaching_journals`
- `teaching_journals` `1 : N` `journal_attendances` (Cascade Delete)
- `users` (Student) `1 : N` `journal_attendances` (Cascade Delete)
- **Unique Constraint**: `uq_journal_student_attendance` pada `(journal_id, student_id)`.

---

## 3. Spesifikasi Endpoint API

Semua endpoint jurnal berada di bawah prefiks `/api/journals` dan diproteksi dengan guard dependency `require_teacher` (hanya pengguna ber-role `teacher` yang dapat mengakses).

### 3.1. Daftar Jurnal Guru
- **Method**: `GET /api/journals/`
- **Query Params**:
  - `class_id` (*optional*, int): Filter berdasarkan ID kelas.
  - `skip` (*optional*, int, default `0`): Paginasi offset.
  - `limit` (*optional*, int, default `100`): Batas jumlah data.
- **Response**: `200 OK` (Array of `JournalListItem`)
```json
[
  {
    "id": 1,
    "uuid": "4c94709f-6829-4ce3-875c-4d3714bfa4d1",
    "teacher_id": 2,
    "class_id": 5,
    "class_name": "X-1",
    "title": "Pertemuan 3 - Stoikiometri Reaksi & Konsep Mol",
    "date": "2026-10-27",
    "start_time": "07:30",
    "end_time": "09:00",
    "planned_materials": [10, 11],
    "completed_materials": [10],
    "total_students": 32,
    "present_students": 30,
    "avg_score": 88.5,
    "created_at": "2026-10-27T08:00:00Z"
  }
]
```

### 3.2. Buat Jurnal Baru
- **Method**: `POST /api/journals/`
- **Request Body** (`JournalCreate`):
```json
{
  "class_id": 5,
  "title": "Pertemuan 3 - Stoikiometri Reaksi & Konsep Mol",
  "date": "2026-10-27",
  "start_time": "07:30",
  "end_time": "09:00",
  "planned_materials": [10, 11],
  "completed_materials": [10],
  "notes": "Siswa perlu latihan tambahan menghitung pereaksi pembatas.",
  "attendances": [
    {
      "student_id": 14,
      "status": "present",
      "score": 90.0,
      "notes": "Tugas selesai tepat waktu"
    },
    {
      "student_id": 15,
      "status": "sick",
      "score": null,
      "notes": "Surat dokter terlampir"
    }
  ]
}
```
- **Response**: `201 Created` (`JournalDetailResponse`)

### 3.3. Ambil Rincian Detail Jurnal
- **Method**: `GET /api/journals/{journal_uuid}`
- **Response**: `200 OK` (`JournalDetailResponse`)

### 3.4. Pembaruan Jurnal
- **Method**: `PATCH /api/journals/{journal_uuid}`
- **Request Body** (`JournalUpdate`): Seluruh field bersifat opsional.
- **Response**: `200 OK` (`JournalDetailResponse`)

### 3.5. Hapus Jurnal
- **Method**: `DELETE /api/journals/{journal_uuid}`
- **Response**: `204 No Content`

---

## 4. Alur Antarmuka Pengguna (Frontend Workflow)

Komponen frontend diimplementasikan pada `frontend/src/views/teacher/JournalManagementView.vue`.

```text
[Dashboard Guru] 
      │
      ▼ (Klik Menu "Jurnal Mengajar")
[JournalManagementView]
   ├── Filter Kelas & Search Bar
   ├── Grid Kartu Riwayat Jurnal
   │     ├── Label Kelas & Tanggal
   │     ├── Judul Sesi & Rentang Jam
   │     ├── Rasio Capaian Materi (Selesai / Target)
   │     ├── Statistik Kehadiran (Hadir / Total Siswa)
   │     ├── Rerata Nilai Tugas Siswa
   │     └── Tombol Aksi [Lihat / Edit] & [Hapus]
   │
   └── Modal Form Terpadu (Buat / Edit)
         ├── Langkah 1: Info Kelas, Tanggal & Rentang Waktu (Jam Mulai - Selesai)
         ├── Langkah 2: Checklist Modul Silabus (Target Pembahasan & Selesai)
         ├── Langkah 3: Presensi Siswa & Input Nilai Tugas (Hadir, Sakit, Izin, Alpa, Skor 0-100, Catatan)
         └── Langkah 4: Refleksi & Kendala Pembelajaran Guru
```

### Validasi & Aturan Bisnis
1. Guru hanya dapat melihat dan mengedit jurnal yang ia buat sendiri (`teacher_id == current_user.id`).
2. Saat kelas dipilih di form modal:
   - Sistem memuat otomatis siswa terdaftar pada kelas (`api.classes.getStudents`).
   - Sistem memuat modul dan materi silabus sesuai tingkat level kelas (`X`, `XI`, `XII`).
3. Skor tugas siswa bersifat opsional dan bertipe `float` dengan rentang `0` sampai `100`.
4. Jika materi dihapus dari target rencana (`planned_materials`), maka status selesainya (`completed_materials`) otomatis dibatalkan.
