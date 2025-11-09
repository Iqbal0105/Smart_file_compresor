from PIL import Image

def compress_image(input_path, output_path, quality=60, max_size=(1280,1280)):
    img = Image.open(input_path)

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(output_path, "JPEG", optimize=True, quality=quality)
