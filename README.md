# Cargo Drone Monitor 🚁📦

Sistem monitoring kargo drone berbasis AI yang mengintegrasikan model deteksi target helipad **YOLOv8**, dasbor telemetri interaktif **Streamlit**, dan penyimpanan basis data **SQLite**. Proyek ini dirancang untuk memantau status pengiriman logistik udara secara *real-time* serta memastikan ketepatan pendaratan otonom.

---

## 🚀 Fitur Utama
* **Deteksi Helipad berbasis YOLOv8:** Identifikasi area pendaratan target secara presisi menggunakan *computer vision*.
* **Dasbor Telemetri Streamlit:** Antarmuka visual interaktif untuk memantau status drone, koordinat, baterai, dan log penerbangan secara *real-time*.
* **Manajemen Basis Data SQLite:** Pencatatan riwayat misi dan data telemetri secara lokal dan efisien.
* **Otomasi Proses Bisnis:** Mendukung integrasi alur kerja logistik modern.

---

## 🛠️ Tech Stack
* **Bahasa Pemrograman:** Python
* **Computer Vision:** Ultralytics YOLOv8
* **Antarmuka Web:** Streamlit
* **Basis Data:** SQLite
* **Kontrol Versi:** Git & GitHub

--- 

## ⚙️ Instalasi & Menjalankan Proyek

1. **Clone repository ini:**
   ```bash
   git clone https://github.com/MRZufarrel/cargo-drone-monitor.git
   cd cargo-drone-monitor
   ```

2. **Buat dan aktifkan *virtual environment* (Opsional tapi disarankan):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependensi yang diperlukan:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan aplikasi Streamlit:**
   ```bash
   streamlit run app.py
   ```

---

## 📄 Lisensi
Proyek ini dilisensikan di bawah **MIT License**. Silakan lihat file [LICENSE](LICENSE) untuk informasi lebih lanjut.
