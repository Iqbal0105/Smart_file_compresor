# main.py
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import os
import uuid
import time
import shutil
import logging

# compress functions (pastikan ada di folder compress/)
from compress.compress_image import compress_image
from compress.compress_pdf import compress_pdf

# ------------- Konfigurasi -------------
APP_HOST = "0.0.0.0"
APP_PORT = 5000
DEBUG = False

INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
ALLOWED_EXT = (".jpg", ".jpeg", ".png", ".pdf", ".docx")

# maksimal ukuran upload (bytes) — ubah sesuai kebutuhan
MAX_UPLOAD_MB = 50
MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

# waktu (detik) untuk menganggap file "lama" dan aman dihapus (misal 5 menit)
FILE_TTL_SECONDS = 5 * 60

# ---------------------------------------

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # (opsional) minimize caching saat development

# buat folder bila belum ada
os.makedirs(INPUT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sfc")

# ---------------- util -----------------
def remove_old_files(folder, older_than_seconds=FILE_TTL_SECONDS):
    """Hapus file-file di folder yang lebih lama dari batas waktu."""
    now = time.time()
    removed = []
    try:
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            try:
                stat = os.stat(path)
            except FileNotFoundError:
                continue
            # gunakan mtime — jika file lebih lama dari threshold hapus
            if now - stat.st_mtime > older_than_seconds:
                try:
                    if os.path.isfile(path) or os.path.islink(path):
                        os.remove(path)
                        removed.append(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path, ignore_errors=True)
                        removed.append(path)
                except Exception as e:
                    logger.warning("Gagal hapus %s: %s", path, e)
    except FileNotFoundError:
        pass
    return removed

def allowed_filename(filename):
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in ALLOWED_EXT)

# --------------- Routes ----------------
@app.route("/")
def index():
    """
    Jangan hapus folder — hanya hapus file lama.
    Ini mencegah race condition saat upload/download lewat tunnel.
    """
    removed_input = remove_old_files(INPUT_FOLDER)
    removed_output = remove_old_files(OUTPUT_FOLDER)
    if removed_input or removed_output:
        logger.info("Removed old files: %s %s", removed_input, removed_output)
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    # Validasi presence file
    if "file" not in request.files:
        return "Tidak ada file yang dikirim (field 'file' tidak ditemukan).", 400

    file = request.files["file"]
    if file.filename == "":
        return "Nama file kosong.", 400

    # Cek ekstensi
    filename_raw = secure_filename(file.filename)
    if not allowed_filename(filename_raw):
        return "Unsupported file type", 400

    # Ambil level (nilai string seperti "60", "40", "20")
    level = request.form.get("level", None)
    try:
        quality = int(level) if level is not None else 60
    except Exception:
        quality = 60

    # Map quality ke preset/pdf_preset dan max_size
    if quality == 60:
        pdf_preset = "/printer"
        max_size = (1280, 1280)
    elif quality == 40:
        pdf_preset = "/ebook"
        max_size = (960, 960)
    else:
        pdf_preset = "/screen"
        max_size = (640, 640)

    # Simpan file ke disk dengan UUID prefix
    file_id = str(uuid.uuid4())
    input_filename = f"{file_id}_{filename_raw}"
    input_path = os.path.join(INPUT_FOLDER, input_filename)

    try:
        file.save(input_path)
    except Exception as e:
        logger.exception("Gagal menyimpan input file: %s", e)
        return "Gagal menyimpan file.", 500

    lower = filename_raw.lower()
    output_path = None

    try:
        if lower.endswith((".jpg", ".jpeg", ".png")):
            output_filename = f"{file_id}_compressed.jpg"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            # compress_image menerima quality dan max_size (pastikan signature sesuai)
            compress_image(input_path, output_path, quality=quality, max_size=max_size)
        elif lower.endswith(".pdf"):
            output_filename = f"{file_id}_compressed.pdf"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            # compress_pdf menerima input_path, output_path, pdf_preset
            compress_pdf(input_path, output_path, pdf_preset)
        elif lower.endswith(".docx"):
            output_filename = f"{file_id}_compressed.docx"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            from compress.compress_docx import compress_docx
            compress_docx(input_path, output_path, quality=quality)
        else:
            # seharusnya tak akan ke sini karena sudah dicek allowed_filename
            raise ValueError("Unsupported file type")
    except Exception as e:
        logger.exception("Gagal kompres file: %s", e)
        # hapus input jika masih ada
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except Exception:
            pass
        return "Gagal memproses file (kompres).", 500

    # Hapus input file setelah kompres (jika masih ada)
    try:
        if os.path.exists(input_path):
            os.remove(input_path)
    except Exception:
        logger.warning("Gagal hapus input file %s", input_path)

    # Redirect ke halaman download
    return redirect(url_for("download_page", filename=os.path.basename(output_path)))

@app.route("/download/<filename>")
def download_page(filename):
    # Pastikan file ada
    full = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(full):
        return "File tidak ditemukan", 404
    return render_template("download.html", filename=filename)

@app.route("/download_file/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File tidak ditemukan", 404
    return send_file(file_path, as_attachment=True)  # hapus conditional=True

# -------------- error handlers --------------
@app.errorhandler(413)
def request_entity_too_large(error):
    return f"File terlalu besar. Maksimum {MAX_UPLOAD_MB} MB.", 413

# -------------- main --------------
if __name__ == "__main__":
    logger.info("Starting Smart File Compressor on %s:%s (debug=%s)", APP_HOST, APP_PORT, DEBUG)
    app.run(host=APP_HOST, port=APP_PORT, debug=DEBUG, threaded=True)
