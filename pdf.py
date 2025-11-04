import pikepdf

def compress_pdf(input_file, output_file, quality=3):
    """
    Compress PDF menggunakan pikepdf.
    quality: 0 (terkecil) - 3 (terbaik)
    """
    optimization = {
        0: pikepdf.ObjectStreamMode.generate,
        1: pikepdf.ObjectStreamMode.generate,
        2: pikepdf.ObjectStreamMode.generate,
        3: pikepdf.ObjectStreamMode.preserve,
    }

    with pikepdf.open(input_file) as pdf:
        pdf.save(
            output_file,
            object_stream_mode=optimization.get(quality, 3),
            linearize=True  # membuat file lebih efisien untuk dibaca
        )
    print(f"✅ PDF berhasil dikompres dan disimpan ke: {output_file}")

# contoh penggunaan
compress_pdf("pdf/lorem.pdf", "pdf/lorem_compressed.pdf", quality=1)
