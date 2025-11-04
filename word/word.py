import zipfile
import os
from PIL import Image
import io
import shutil

# Path file Word
input_file = "Kuis.doc"
output_file = "dokumen_kompres.docx"

# Buat folder sementara untuk ekstraksi
temp_dir = "temp_docx"
if os.path.exists(temp_dir):
    shutil.rmtree(temp_dir)
os.mkdir(temp_dir)

# Ekstrak isi file .docx (karena isinya ZIP)
with zipfile.ZipFile(input_file, 'r') as zip_ref:
    zip_ref.extractall(temp_dir)

# Kompres semua gambar dalam folder "word/media"
media_path = os.path.join(temp_dir, "word", "media")
if os.path.exists(media_path):
    for file_name in os.listdir(media_path):
        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):
            file_path = os.path.join(media_path, file_name)

            # Buka gambar dan kompres ulang dengan kualitas 70
            img = Image.open(file_path)
            img = img.convert("RGB")

            compressed_io = io.BytesIO()
            img.save(compressed_io, format="JPEG", quality=70, optimize=True)
            with open(file_path, "wb") as f:
                f.write(compressed_io.getvalue())

# Buat ulang file .docx yang sudah dikompres
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
    for root, _, files in os.walk(temp_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, temp_dir)
            docx_zip.write(full_path, rel_path)

# Hapus folder sementara
shutil.rmtree(temp_dir)

print(f"✅ File Word berhasil dikompres dan disimpan sebagai '{output_file}'")
