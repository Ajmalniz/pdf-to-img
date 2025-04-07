import streamlit as st
from PIL import Image
import fitz  # PyMuPDF
import os
import tempfile
import base64
import shutil

# File conversion functions
def convert_image_to_pdf(image_path: str) -> str:
    try:
        image = Image.open(image_path)
        pdf_path = image_path.rsplit(".", 1)[0] + ".pdf"
        image.save(pdf_path, "PDF", resolution=100.0)
        return pdf_path
    except Exception as e:
        st.error(f"Error converting image to PDF: {e}")
        return None

def convert_pdf_to_images(pdf_path: str) -> list:
    try:
        doc = fitz.open(pdf_path)
        image_paths = []
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            image_path = f"{pdf_path.rsplit('.', 1)[0]}_page_{i + 1}.png"
            pix.save(image_path)
            image_paths.append(image_path)
        doc.close()
        return image_paths
    except Exception as e:
        st.error(f"Error converting PDF to images: {e}")
        return []

def smart_convert(file_path: str):
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        pdf_path = convert_image_to_pdf(file_path)
        return "pdf", pdf_path if pdf_path else None
    elif ext == ".pdf":
        images = convert_pdf_to_images(file_path)
        return "images", images
    else:
        return "error", "Unsupported file format."

# Streamlit frontend
st.set_page_config(page_title="Image ⇄ PDF Converter", layout="centered")
st.title("Image ⇄ PDF Converter")

uploaded_file = st.file_uploader("Upload an image or a PDF", type=["jpg", "jpeg", "png", "bmp", "pdf"])

if uploaded_file is not None:
    # Create a temporary directory to store files
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        result_type, result = smart_convert(file_path)

        if result_type == "pdf" and result:
            st.success("Converted to PDF!")
            with open(result, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<a href="data:application/pdf;base64,{base64_pdf}" download="converted.pdf">Download PDF</a>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                # Optional: Preview PDF in iframe
                st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500"></iframe>', unsafe_allow_html=True)

        elif result_type == "images" and result:
            st.success("Converted to Images!")
            for img_path in result:
                st.image(img_path, caption=os.path.basename(img_path))
                with open(img_path, "rb") as f:
                    b64_img = base64.b64encode(f.read()).decode()
                    href = f'<a href="data:file/png;base64,{b64_img}" download="{os.path.basename(img_path)}">Download Image</a>'
                    st.markdown(href, unsafe_allow_html=True)

        elif result_type == "error":
            st.error("Unsupported file format.")
        else:
            st.error("Conversion failed. Please try again.")

    # No need to manually delete files; TemporaryDirectory handles cleanup