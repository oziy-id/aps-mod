<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=APSMod%20CMS&fontSize=80&animation=fadeIn&fontAlignY=35&desc=Premium%20App%20Store%20Management%20System&descAlignY=55&descAlign=50"/>

  <br>

  <img src="https://img.shields.io/badge/Built%20With-Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/Database-Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white" />
  <img src="https://img.shields.io/badge/Frontend-Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" />
  <img src="https://img.shields.io/badge/Deploy-Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" />
  <br>
  <img src="https://img.shields.io/github/license/oziy-id/apsmod?style=flat-square&color=blue" />
  <img src="https://img.shields.io/github/repo-size/oziy-id/apsmod?style=flat-square&color=green" />
</div>

---

## 📖 About The Project

**APSMod** adalah Content Management System (CMS) modern yang dirancang khusus untuk mengelola situs download aplikasi Android (APK/Mod). Dibangun dengan performa dan keamanan sebagai prioritas utama.

Website ini memungkinkan Admin/Owner untuk mempublikasikan aplikasi, mengelola link download, memantau statistik secara real-time, dan mengatur tim (partner) dengan sistem keamanan berlapis.

### ✨ Key Features

* **👑 Powerful Admin Dashboard**: Kontrol penuh untuk Upload, Update, dan Delete aplikasi.
* **☁️ Supabase Storage Integration**: Penyimpanan gambar (Icon & Screenshot) yang aman, cepat, dan terpusat di Cloud.
* **🧹 Smart Auto-Clean**: Sistem otomatis menghapus file sampah di Storage saat aplikasi dihapus dari database.
* **🔄 Instant Updates**: Fitur update Link Download & Versi aplikasi tanpa perlu input ulang data gambar/deskripsi.
* **📊 Real-time Analytics**: Penghitung jumlah download yang akurat dan daftar aplikasi terpopuler.
* **🔐 Secure Authentication**: Sistem login aman dengan hashing password dan manajemen sesi.
* **👥 Partner System with OTP**: Rekrut tim admin baru menggunakan Kode OTP (One-Time Password) yang dinamis.
* **📱 Responsive Design**: Tampilan UI/UX yang elegan dan responsif di semua perangkat (Mobile/Desktop).
* **📧 Email Notification**: Formulir kontak yang terintegrasi langsung dengan Gmail Anda (SMTP).

---

## 🛠️ Tech Stack

* **Backend Framework**: Python Flask
* **Database**: PostgreSQL (via Supabase)
* **File Storage**: Supabase Storage Buckets
* **ORM**: SQLAlchemy
* **Frontend**: HTML5, Jinja2, Tailwind CSS (CDN), JavaScript
* **Deployment**: Vercel (Serverless Function)

---

## 🚀 Getting Started (Localhost)

Ingin menjalankan project ini di komputer Anda? Ikuti langkah mudah berikut:

### 1. Prerequisites
Pastikan Anda sudah menginstal:
* Python 3.9+
* Git
* Akun Supabase & Gmail (untuk fitur email)

### 2. Installation

1.  **Clone Repository**
    ```bash
    git clone [https://github.com/oziy-id/apsmod.git](https://github.com/oziy-id/apsmod.git)
    cd apsmod
    ```

2.  **Buat Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Environment Variables (.env)**
    Buat file bernama `.env` di folder root project, lalu isi dengan data Anda:
    ```ini
    # Kunci Keamanan Flask (Bebas acak)
    SECRET_KEY=rahasia_super_aman_123

    # Database URL (Dari Supabase > Settings > Database > Connection String > URI)
    # Ganti [YOUR-PASSWORD] dengan password database Anda
    DATABASE_URL=postgresql://postgres.xxxx:YOUR-PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres

    # Konfigurasi Supabase (Dari Project Settings > API)
    SUPABASE_URL=[https://xyzcompany.supabase.co](https://xyzcompany.supabase.co)
    SUPABASE_KEY=eyJh... (Gunakan Service_Role / Secret Key agar bisa upload/delete)

    # Konfigurasi Email (Gunakan App Password Gmail, bukan password login biasa)
    MAIL_USERNAME=email_anda@gmail.com
    MAIL_PASSWORD=kode_app_password_16_digit
    MAIL_RECIPIENT=email_penerima_laporan@gmail.com
    
    # Kode OTP Awal untuk Registrasi Partner
    INVITE_CODE=6453
    ```

5.  **Jalankan Aplikasi**
    ```bash
    python app.py
    ```
    Buka browser dan akses: `http://127.0.0.1:5000`

---

## ☁️ Deployment (Vercel)

Project ini sudah dikonfigurasi (`vercel.json`) untuk berjalan mulus di Vercel.

1.  Upload kode ke GitHub.
2.  Buka Dashboard Vercel > **Add New Project**.
3.  Import repository GitHub Anda.
4.  Di bagian **Environment Variables**, masukkan semua variabel yang ada di file `.env` tadi.
5.  Klik **Deploy**.
6.  Selesai! Website Anda live.

---

## 📸 Screenshots

| Home Page | Admin Dashboard |
|:---:|:---:|
| <img src="/static/view.jpg" alt="Home" width="300"/> | <img src="/static/admin_dashboard.jpg" alt="Dashboard" width="300"/> |

| App Detail | Mobile View |
|:---:|:---:|
| <img src="/static/detail_app.jpg" alt="Detail" width="300"/> | <img src="/static/mobile_view.jpg" alt="Mobile" width="300"/> |

---

## 🤝 Contributing

Kontribusi sangat diterima! Jika Anda punya ide fitur baru:
1.  Fork project ini.
2.  Buat branch fitur baru (`git checkout -b fitur-keren`).
3.  Commit perubahan Anda (`git commit -m 'Menambahkan fitur keren'`).
4.  Push ke branch (`git push origin fitur-keren`).
5.  Buka Pull Request.

---

## 📝 License

Didistribusikan di bawah Lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.

```text
MIT License
Copyright (c) 2026 Ozi Official
