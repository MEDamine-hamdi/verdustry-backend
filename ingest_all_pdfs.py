import os
from pypdf import PdfReader
import requests

API_URL = "http://localhost:8000/api/v1"
TOKEN = "PASTE_YOUR_ADMIN_JWT_HERE"

PDF_FOLDER = r"regulatory_pdfs"  # ajustez si vos PDF sont ailleurs

FILES = {
    "CELEX_32022L2464_FR_TXT.pdf": "CSRD_Directive_2022_2464",
    "cellar_bc4dcea4-9584-11ec-b4e4-01aa75ed71a1.0002.02_DOC_1.pdf": "CSDDD_Proposal_2022",
    "OJ_L_202490241_FR_TXT.pdf": "ESRS_Corrigendum_2024",
    "OJ_L_202502083_FR_TXT.pdf": "CBAM_Amendment_2025_2083",
    "GRI 1  Fondation 2021 - French.pdf": "GRI_1_Fondation_2021",
    "GRI 2  Informations générales 2021 - French.pdf": "GRI_2_InfosGenerales_2021",
    "GRI 3  Thèmes pertinents 2021 - French.pdf": "GRI_3_ThemesPertinents_2021",
    "GRI 302  Énergie 2016 - French.pdf": "GRI_302_Energie_2016",
    "GRI 305  Émissions 2016 - French.pdf": "GRI_305_Emissions_2016",
}


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def ingest(source_ref: str, text: str):
    res = requests.post(
        f"{API_URL}/assistant/ingest-regulatory",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        json={"sourceRef": source_ref, "text": text},
    )
    print(f"  -> {res.status_code}: {res.text[:200]}")


if __name__ == "__main__":
    for filename, source_ref in FILES.items():
        path = os.path.join(PDF_FOLDER, filename)
        if not os.path.exists(path):
            print(f"SKIP (not found): {filename}")
            continue
        print(f"Processing: {filename}")
        text = extract_text(path)
        print(f"  Extracted {len(text)} characters")
        ingest(source_ref, text)