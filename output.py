# output.py
import pandas as pd
from typing import List, Dict
import os

def save_to_csv(structs: List[Dict], out_path: str = "extracted_news.csv"):
    df = pd.DataFrame(structs)
    df.to_csv(out_path, index=False)
    print("Saved CSV:", out_path)

# Google Sheets optional (requires service account JSON)
def save_to_gsheet(structs: List[Dict], sheet_name: str = "NewsExtraction", creds_json_path: str = None):
    if creds_json_path is None:
        creds_json_path = os.getenv("GSPREAD_JSON_PATH")
    if not creds_json_path or not os.path.exists(creds_json_path):
        raise RuntimeError("Google Sheets credentials not found. Set GSPREAD_JSON_PATH to service account JSON path.")
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json_path, scope)
    client = gspread.authorize(creds)
    try:
        sheet = client.open(sheet_name).sheet1
    except Exception:
        sheet = client.create(sheet_name).sheet1
    # Convert to 2D list with header
    df = pd.DataFrame(structs)
    header = list(df.columns)
    rows = df.fillna("").astype(str).values.tolist()
    sheet.clear()
    sheet.append_row(header)
    for r in rows:
        sheet.append_row(r)
    print("Saved to Google Sheet:", sheet_name)
