import zipfile
import os
import io
from PIL import Image
import shutil

def compress_docx(input_path, output_path, quality=70):
    """
    Kompres gambar di dalam file DOCX tanpa mengubah teks atau struktur dokumen.
    """
    temp_dir = "temp_docx"
    os.makedirs(temp_dir, exist_ok=True)

    # Ekstrak isi file DOCX
    with zipfile.ZipFile(input_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    media_path = os.path.join(temp_dir, "word", "media")

    if os.path.exists(media_path):
        for filename in os.listdir(media_path):
            file_path = os.path.join(media_path, filename)

            try:
                with Image.open(file_path) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format="JPEG", optimize=True, quality=quality)
                    img_bytes.seek(0)

                    with open(file_path, "wb") as f:
                        f.write(img_bytes.read())
            except Exception as e:
                print(f"Gagal kompres gambar {filename}: {e}")

    # Repack DOCX
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                docx_zip.write(full_path, rel_path)

    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✅ DOCX berhasil dikompres (quality={quality})")
