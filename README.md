# Image to PDF Converter

Tool sederhana untuk mengubah satu atau banyak gambar menjadi satu file PDF.

## Versi Web Tanpa Instalasi

Buka file `index.html` di browser, lalu pilih atau drop gambar dan klik **Buat PDF**.

Fitur:

- Bisa menggabungkan banyak gambar menjadi satu PDF.
- Bisa mengubah urutan gambar.
- Bisa memilih ukuran halaman: mengikuti gambar, A4, atau Letter.
- Berjalan lokal di browser tanpa upload file.

## Versi CLI Python

## Setup

```powershell
python -m pip install -r requirements.txt
```

## Contoh Penggunaan

Konversi satu gambar:

```powershell
python image_to_pdf.py foto.jpg
```

Konversi beberapa gambar menjadi satu PDF:

```powershell
python image_to_pdf.py halaman1.png halaman2.png halaman3.jpg -o hasil.pdf
```

Konversi semua gambar dalam folder:

```powershell
python image_to_pdf.py .\gambar -o dokumen.pdf
```

Konversi folder beserta subfolder:

```powershell
python image_to_pdf.py .\gambar -r -o dokumen.pdf
```

Format yang didukung: BMP, GIF, JPEG, PNG, TIFF, dan WEBP.

## Versi Bot Telegram

Bot Telegram menerima gambar dari user, menyimpannya sementara, lalu membuat satu PDF saat user mengetik `/done`.

### Buat Bot

1. Buka Telegram dan chat ke `@BotFather`.
2. Jalankan `/newbot`.
3. Ikuti instruksi sampai mendapatkan token bot.

### Jalankan Di Lokal / VPS

Install dependency:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Atur token bot:

```bash
export TELEGRAM_BOT_TOKEN="ISI_TOKEN_DARI_BOTFATHER"
```

Jalankan bot:

```bash
python bot.py
```

### Cara Pakai Bot

1. Kirim `/start` ke bot.
2. Kirim satu atau beberapa gambar.
3. Kirim `/done` untuk membuat PDF.
4. Kirim `/cancel` untuk membatalkan antrean gambar.
5. Kirim `/status` untuk melihat jumlah gambar yang sudah diterima.

### Jalankan 24 Jam Dengan PM2

Install PM2 jika belum ada:

```bash
npm install -g pm2
```

Pastikan dependency Python sudah terpasang:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Jalankan bot dengan PM2:

```bash
TELEGRAM_BOT_TOKEN="ISI_TOKEN_DARI_BOTFATHER" pm2 start ecosystem.config.js
```

Simpan proses PM2 agar otomatis hidup lagi setelah VPS restart:

```bash
pm2 save
pm2 startup
```

Perintah berguna:

```bash
pm2 status
pm2 logs image-to-pdf-bot
pm2 restart image-to-pdf-bot
pm2 stop image-to-pdf-bot
pm2 delete image-to-pdf-bot
```
