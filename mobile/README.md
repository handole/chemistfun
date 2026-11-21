# KimiFun Mobile (Flutter)

Aplikasi mobile Android/iOS untuk platform pembelajaran kimia KimiFun dengan fungsionalitas yang sejalan dengan versi web.

## Struktur Folder
```text
mobile/
├── pubspec.yaml                 # Dependencies (http, shared_preferences, intl)
└── lib/
    ├── main.dart                # Entry point, routing sesi, & tema aplikasi
    ├── api/
    │   ├── api_config.dart      # Konfigurasi base URL API backend
    │   └── api_service.dart     # Service HTTP client JWT & token storage
    ├── models/
    │   └── user.dart            # Model User (role: teacher / student)
    └── screens/
        ├── auth/
        │   └── login_screen.dart        # Login, Register, & Validasi Kode Guru
        ├── teacher/
        │   └── teacher_home_screen.dart # Manajemen Kelas & Jurnal Mengajar Guru
        └── student/
            └── student_home_screen.dart # Modul Pembelajaran, Kelas Siswa, & KimiBot AI
```

## Fitur & Pemisahan Role

### 1. Role Guru (`teacher`)
- **Login & Register**: Wajib memasukkan kode undangan guru jika mendaftar role guru.
- **Manajemen Kelas**: Membuat kelas kimia baru berdasarkan tingkat (X, XI, XII), melihat kode kelas dan jumlah siswa.
- **Jurnal Mengajar**: Memantau riwayat jurnal, presensi kehadiran siswa per kelas, dan status materi yang diajarkan.

### 2. Role Siswa (`student`)
- **Modul & Materi Pembelajaran**: Membaca materi kimia interaktif per tingkat kelas.
- **Kelasku**: Bergabung ke kelas guru menggunakan kode kelas unik.
- **KimiBot AI**: Chatbot AI interaktif untuk konsultasi konsep dan reaksi kimia secara real-time.

## Cara Menjalankan

1. Masuk ke direktori `mobile`:
   ```bash
   cd mobile
   ```

2. Unduh dependencies Flutter:
   ```bash
   flutter pub get
   ```

3. Jalankan aplikasi:
   - Di emulator Android:
     ```bash
     flutter run
     ```
   - Dengan target URL backend kustom (misal Tailscale atau VPS):
     ```bash
     flutter run --dart-define=BASE_URL="https://handole-pc.tail39a9bf.ts.net/api"
     ```
