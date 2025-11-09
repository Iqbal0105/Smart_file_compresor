import subprocess
import platform

def get_ghostscript_command():
    system = platform.system().lower()
    if "windows" in system:
        return "gswin64c"  # atau "gswin32c"
    return "gs"  # untuk Linux / macOS

def compress_pdf(input_path, output_path, pdf_preset="/screen"):
    command = [
        get_ghostscript_command(),
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-dPDFSETTINGS={pdf_preset}",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ PDF dikompres menggunakan Ghostscript preset {pdf_preset}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal kompres PDF: {e}")
