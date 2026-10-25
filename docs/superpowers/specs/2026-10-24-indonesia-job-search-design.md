# Adaptasi pencarian kerja Indonesia

Tanggal: 24 Oktober 2026
Status: disetujui pengguna pada 24 Oktober 2026; implementasi diotorisasi
Basis: commit e16acee, ai-job-search-dev/ai-job-search

## Tujuan dan batas perubahan

Menyesuaikan workspace yang sudah ada untuk pencari kerja di Indonesia. Pengguna memilih konfigurasi Indonesia + perbaikan logika dan pengujian. Ini penyesuaian konfigurasi, aturan evaluasi, dan kode pendukung; tidak melatih ulang model AI.

Tetap memakai alur profil -> pencarian -> deduplikasi -> penilaian -> dokumen lamaran. Tidak membangun aplikasi web, memasang dependensi, mengirim lamaran, atau mengisi profil pribadi tanpa data pengguna.

## Pendekatan yang dipertimbangkan

1. Panduan dan konfigurasi saja: perubahan ringan, tetapi tidak memperbaiki hasil salah dari deduplikasi dan default penilaian.
2. Konfigurasi + perbaikan logika + pengujian: dipilih pengguna. Memperbaiki perilaku yang dapat dibuktikan tanpa mengganti arsitektur repo.

## Temuan audit yang sudah dibuktikan

- tools/scrape_state.py membuang hit kedua jika perusahaan dan jabatan sama walaupun kota dan URL berbeda. Simulasi Admin/PT Contoh di Bandung dan Surabaya menghasilkan satu dari dua lowongan.
- tools/job_key.py memberi kunci yang sama untuk perusahaan + jabatan tersebut. Membetulkan seleksi saja belum cukup: penyimpanan harus membedakan lowongan tanpa mengganti kunci riwayat lama.
- tools/rank_state.py memberi PASS ketika location_verdict atau language_gate tidak dikirim. Simulasi skor 80 tanpa kedua keputusan tetap masuk ranked sebagai PASS/PASS.
- Aturan lokasi di 04-job-evaluation.md menganggap relokasi selalu FAIL dan remote dengan sesekali ke kantor selalu PASS. Keputusan seharusnya mengikuti kesediaan kandidat serta lokasi kantor dan cakupan remote yang dinyatakan.
- search-queries.md masih generik. JobStreet Indonesia, Glints, Dealls, dan Kalibrr belum memiliki integrasi pencarian lokal bawaan.
- Portal Denmark sudah enabled: false, sehingga tidak perlu dinonaktifkan ulang.
- Uji akses LinkedIn sebelumnya mendapat 429. Pencarian web dan teks lowongan manual perlu tetap menjadi jalur yang berfungsi.
- Baseline: 138 pengujian terpilih dijalankan, 135 lulus dan 3 dilewati.

## Perubahan yang diusulkan

### 1. Satu panduan pasar Indonesia

Tambahkan panduan pasar Indonesia yang dirujuk dari setup, pencarian, penilaian, dan dokumentasi penggunaan. Targetkan Indonesia, gunakan Bahasa Indonesia untuk interaksi, dan pertahankan pilihan bahasa CV serta tingkat bahasa sebagai data kandidat yang harus dikonfirmasi.

Profil tetap memakai placeholder. Kota, batas perjalanan, relokasi, jabatan, pendidikan, senioritas, kontrak, dan gaji minimum tidak diisi dengan asumsi pribadi. Contoh kota atau profesi ditandai sebagai contoh.

### 2. Pencarian lokal yang realistis

Sediakan template pencarian JobStreet Indonesia, Glints, Dealls, Kalibrr, LinkedIn, dan laman karier perusahaan. Gunakan pencarian web sebagai fallback untuk portal tanpa CLI; jangan mengklaim sudah ada scraper/API lokal yang berhasil diuji.

Variasi kata kunci memakai jabatan dan fungsi dalam bahasa yang dikuasai kandidat. Cantumkan opsi fresh graduate, magang, staff, supervisor, serta nonteknis tanpa mengaktifkannya untuk setiap kandidat. Freehire dipakai untuk kebutuhan teknologi. Saat portal 429/403, catat kegagalan dan beralih sumber, bukan mengulang tanpa batas.

Sumber lokal yang telah diperiksa: https://id.jobstreet.com/jobs, https://glints.com/id, https://dealls.com/. Kalibrr akan diverifikasi sebelum templatenya difinalisasi.

### 3. Deduplikasi yang menjaga kesempatan dan riwayat

URL identik tetap deduplikat. Perusahaan + jabatan tetap dibandingkan, tetapi lokasi berbeda yang diketahui tidak boleh otomatis dibuang. Lokasi yang tidak tersedia tetap diperlakukan konservatif agar tidak menggandakan hasil lama tanpa bukti.

Simpan lowongan tambahan dengan kunci pembeda stabil saat kunci perusahaan + jabatan bertabrakan. Jangan mengganti kunci entri lama. Ranking tetap memakai kunci yang diberikan state. Pemeriksaan tracker perusahaan + jabatan tetap konservatif karena tracker lama belum mempunyai lokasi terstruktur; dokumentasikan batas ini.

### 4. Penilaian yang menampilkan ketidakpastian

Keputusan lokasi atau bahasa yang tidak dikirim diberi FLAG dengan alasan perlu diperiksa, bukan PASS. Pertahankan kompatibilitas verdict lokasi lama yang valid. Verdict tidak dikenal tetap error.

Relokasi mengikuti pilihan kandidat. Remote harus memeriksa penerimaan pelamar dari Indonesia dan kebutuhan hadir ke kantor. Informasi lokasi, gaji, kontrak, bahasa, dan persyaratan yang tidak disebutkan dicatat sebagai belum diketahui, tidak ditebak.

### 5. Penyesuaian evaluasi Indonesia

Catat jenjang pendidikan yang relevan (SMA/SMK, D3/D4, S1/S2), peluang fresh graduate, pengalaman magang/proyek yang benar-benar dimiliki, status kontrak (tetap, kontrak, outsourcing, magang, freelance), shift, dan penempatan.

Tampilkan gaji sebagaimana disebutkan: IDR/Rp, bulanan/tahunan, rentang, serta gross/net/THP hanya ketika diketahui. Jangan mengubah mata uang atau periode tanpa dasar; gaji tersembunyi bukan gagal otomatis. THR/BPJS/tunjangan dicatat hanya jika disebutkan, tanpa menambahkan asumsi manfaat atau kesimpulan hukum.

Sinyal biaya rekrutmen, identitas pemberi kerja yang tidak jelas, atau permintaan dokumen sensitif ditampilkan sebagai hal yang perlu diverifikasi; bukan putusan bahwa perusahaan pasti penipu. Lamaran tetap disiapkan dengan fakta kandidat yang terverifikasi.

## Verifikasi dan kriteria selesai

- Tambahkan regresi untuk kota berbeda, URL sama, kunci bertabrakan, dan riwayat lama yang tidak berubah.
- Tambahkan regresi untuk verdict hilang/null/kosong, FAIL yang tetap memveto, dan keputusan eksplisit yang tetap dipertahankan.
- Jalankan pengujian kode yang berubah, pemeriksaan konsistensi spesifikasi, pemeriksaan versi framework bila file berversi berubah, lalu pengujian Python repo yang relevan.
- Periksa diff akhir dan pastikan tidak ada data kandidat yang dibuat-buat atau dependensi baru yang diperlukan.
- Laporkan perubahan, hasil uji, serta batas integrasi portal yang belum diuji secara langsung.
