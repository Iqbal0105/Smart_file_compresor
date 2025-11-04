import zipfile
import os

# Nama file input dan output
input_file = "Data.xlsx"
output_file = "Data_compressed.xlsx"

# Pastikan file ada
if not os.path.exists(input_file):
    print(f"❌ File '{input_file}' tidak ditemukan.")
else:
    # Buka file xlsx (sebenarnya ZIP)
    with zipfile.ZipFile(input_file, 'r') as zip_ref:
        # Ekstrak semua isi ke folder sementara
        zip_ref.extractall("temp_excel")

    # Kompres ulang dengan tingkat kompresi maksimal
    with zipfile.ZipFile(output_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zip_out:
        for foldername, subfolders, filenames in os.walk("temp_excel"):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, "temp_excel")
                zip_out.write(filepath, arcname)

    # Hapus folder sementara
    import shutil
    shutil.rmtree("temp_excel")

    print(f"✅ File berhasil dikompres: {output_file}")