from PyPDF2 import PdfReader
import re
import os


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_resume_data(pdf_path):
    text = extract_text_from_pdf(pdf_path)

    # Email
    email_match = re.search(
        r'[\w\.-]+@[\w\.-]+\.\w+',
        text
    )
    email = email_match.group(0) if email_match else ""

    # Phone
    phone_match = re.search(
        r'(?:\+91[\s-]?)?[6-9]\d{9}',
        text
    )
    phone = phone_match.group(0) if phone_match else ""

    # Name - first non-empty line
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    name = "Unknown"

    if lines:
        name = lines[0]

    # If first line is not a good name, use PDF filename
    if name == "Unknown" or "resume" in name.lower():
        filename = os.path.basename(pdf_path)
        name = os.path.splitext(filename)[0]
        name = name.replace("_", " ").replace("-", " ")

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": "BCA",
        "experience": "Fresher"
    }