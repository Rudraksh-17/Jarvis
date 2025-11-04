
import os
import io
import cv2
import fitz  # PyMuPDF
import gzip
import zipfile
import shutil
import random
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
from datetime import datetime

# ------------ CONFIG ------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

st.set_page_config(page_title="File Compressor", page_icon="🗜️", layout="centered")

# ------------ HELPERS ------------

def compress_pdf(input_pdf_path, output_pdf_path):
    """Compress images inside a PDF using PyMuPDF + OpenCV; return True/False."""
    try:
        doc = fitz.open(input_pdf_path)
        for page_num, page in enumerate(doc):
            images = page.get_images(full=True)
            for img in images:
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image.get("ext", "")

                    nparr = np.frombuffer(image_bytes, np.uint8)
                    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if img_cv is None:
                        continue

                    # Re-encode large non-JPEGs to JPEG(30)
                    if ext.lower() != 'jpeg' and len(image_bytes) > 100_000:
                        ok, compressed = cv2.imencode('.jpg', img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                        if ok:
                            new_xref = doc.insert_image_stream(
                                compressed.tobytes(),
                                width=img_cv.shape[1],
                                height=img_cv.shape[0]
                            )
                            page.replace_image(xref, new_xref)
                except Exception as e:
                    print(f"Image compress error on page {page_num}: {e}")
        # Save linearized & cleaned
        doc.save(output_pdf_path, garbage=4, deflate=True, clean=True, linear=True)
        doc.close()
        return True
    except Exception as e:
        print(f"PDF compression error: {e}")
        return False


def compress_csv(input_ss_path):
    output_csv_path = input_ss_path.replace('.csv', '.csv.gz')
    with open(input_ss_path, 'rb') as f_in, gzip.open(output_csv_path, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    return output_csv_path


def compress_xlsx(input_ss_path, quality_jpeg=40):
    temp_dir = os.path.join(UPLOADS_DIR, 'temp_xlsx')
    os.makedirs(temp_dir, exist_ok=True)
    output_xlsx_path = input_ss_path.replace('.xlsx', '_compressed.xlsx')

    with zipfile.ZipFile(input_ss_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    media_dir = os.path.join(temp_dir, 'xl', 'media')
    if os.path.exists(media_dir):
        for fname in os.listdir(media_dir):
            fpath = os.path.join(media_dir, fname)
            try:
                img = Image.open(fpath)
                img = img.convert('RGB')
                img.save(fpath, format='JPEG', quality=quality_jpeg)
            except Exception as e:
                print(f"Skipped media {fname}: {e}")

    with zipfile.ZipFile(output_xlsx_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                zipf.write(full_path, rel_path)

    shutil.rmtree(temp_dir, ignore_errors=True)
    return output_xlsx_path


def convert_and_compress_xls(input_ss_path):
    df = pd.read_excel(input_ss_path, engine='xlrd')
    xlsx_path = input_ss_path.replace('.xls', '.xlsx')
    df.to_excel(xlsx_path, index=False)
    return compress_xlsx(xlsx_path)


def compress_images_in_docx(input_docx, output_docx, quality=60):
    temp_dir = os.path.join(UPLOADS_DIR, "temp_docx")
    media_folder = os.path.join(temp_dir, 'word', 'media')

    with zipfile.ZipFile(input_docx, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    if os.path.exists(media_folder):
        for img_file in os.listdir(media_folder):
            img_path = os.path.join(media_folder, img_file)
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=quality)
                    with open(img_path, 'wb') as f:
                        f.write(buf.getvalue())
            except Exception as e:
                print(f"DOCX media skip {img_file}: {e}")

    with zipfile.ZipFile(output_docx, 'w', compression=zipfile.ZIP_DEFLATED) as docx:
        for foldername, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, temp_dir)
                docx.write(file_path, arcname)

    shutil.rmtree(temp_dir, ignore_errors=True)


def compress_images_in_pptx(input_pptx, output_pptx, quality=60):
    temp_dir = os.path.join(UPLOADS_DIR, "temp_pptx")
    media_folder = os.path.join(temp_dir, 'ppt', 'media')

    with zipfile.ZipFile(input_pptx, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    if os.path.exists(media_folder):
        for img_file in os.listdir(media_folder):
            img_path = os.path.join(media_folder, img_file)
            try:
                with Image.open(img_path) as img:
                    img = img.convert('RGB')
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=quality)
                    with open(img_path, 'wb') as f:
                        f.write(buf.getvalue())
            except Exception as e:
                print(f"PPTX media skip {img_file}: {e}")

    with zipfile.ZipFile(output_pptx, 'w', compression=zipfile.ZIP_DEFLATED) as pptx:
        for foldername, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, temp_dir)
                pptx.write(file_path, arcname)

    shutil.rmtree(temp_dir, ignore_errors=True)


# ------------ STREAMLIT UI ------------
st.title("🗜️ File Compressor")
st.caption("PDF, Excel (xls/xlsx/csv), Word (docx), and PowerPoint (pptx) compressor")

with st.expander("Upload files", expanded=True):
    files = st.file_uploader(
        "Choose file(s)",
        type=["pdf", "csv", "xlsx", "xls", "docx", "pptx"],
        accept_multiple_files=True
    )
    quality_docx_pptx = st.slider("Image quality for DOCX/PPTX (lower = smaller)", 20, 95, 60)
    quality_xlsx = st.slider("Image quality inside XLSX (lower = smaller)", 20, 95, 40)

run = st.button("Compress")

if run:
    if not files:
        st.error("No files selected.")
    else:
        results = []
        for uploaded_file in files:
            try:
                fname = uploaded_file.name
                ext = os.path.splitext(fname)[1].lower()
                serial = random.randint(10000, 99999)
                in_path = os.path.join(UPLOADS_DIR, fname)
                with open(in_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())

                if ext == '.pdf':
                    out_name = f"compressed_{serial}.pdf"
                    out_path = os.path.join(UPLOADS_DIR, out_name)
                    ok = compress_pdf(in_path, out_path)
                    if not ok:
                        results.append((fname, None, "PDF compression failed"))
                        continue
                elif ext == '.csv':
                    out_path = compress_csv(in_path)
                    out_name = os.path.basename(out_path)
                elif ext == '.xlsx':
                    out_path = compress_xlsx(in_path, quality_jpeg=quality_xlsx)
                    out_name = os.path.basename(out_path)
                elif ext == '.xls':
                    out_path = convert_and_compress_xls(in_path)
                    out_name = os.path.basename(out_path)
                elif ext == '.docx':
                    out_name = f"compressed_{serial}.docx"
                    out_path = os.path.join(UPLOADS_DIR, out_name)
                    compress_images_in_docx(in_path, out_path, quality=quality_docx_pptx)
                elif ext == '.pptx':
                    out_name = f"compressed_{serial}.pptx"
                    out_path = os.path.join(UPLOADS_DIR, out_name)
                    compress_images_in_pptx(in_path, out_path, quality=quality_docx_pptx)
                else:
                    results.append((fname, None, f"Unsupported type: {ext}"))
                    continue

                with open(out_path, 'rb') as f:
                    data = f.read()
                results.append((fname, (out_name, data), None))

            except Exception as e:
                results.append((uploaded_file.name, None, str(e)))

        st.subheader("Results")
        for orig, out_tuple, err in results:
            if err:
                st.write(f"❌ {orig}: {err}")
            else:
                out_name, data = out_tuple
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"✅ {orig} → **{out_name}**")
                with col2:
                    st.download_button(
                        "Download",
                        data=data,
                        file_name=out_name,
                        mime="application/octet-stream",
                        use_container_width=True
                    )

st.markdown("---")
st.caption(f"Build time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
