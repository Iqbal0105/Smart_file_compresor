from PIL import Image

# Buka gambar
img = Image.open("1.jpg")

# Simpan dengan kualitas rendah agar lebih kecil ukuran file-nya
img.save("foto_burik.jpg", quality=10, optimize=True)

print("Foto berhasil dikompres (ukuran tetap sama, tapi jadi burik).")
