import io, json, sys, zipfile, time
from datetime import datetime, timedelta
import requests
import pdfplumber

EDINET_API_KEY = "33aaeba307904ac4a08737145f707e80"
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"

CACHE = {
    "トヨタ自動車": ("E02144", "72030", "S100VWVY"),
    "トヨタ": ("E02144", "72030", "S100VWVY"),
    "メルカリ": ("E33861", "40990", None),
    "HODL1": ("E05320", "37190", None),
    "株式会社HODL1": ("E05320", "37190", None),
}

def get_doc_id(edinet_code):
    for delta in range(400):
        date_str = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            r = requests.get(BASE_URL + "/documents.json",
                params={"date": date_str, "type": 2, "Subscription-Key": EDINET_API_KEY},
                timeout=10)
            if r.status_code != 200:
                time.sleep(0.1)
                continue
            for doc in r.json().get("results", []):
                if (doc.get("edinetCode") == edinet_code
                        and doc.get("ordinanceCode") == "010"
                        and doc.get("formCode") == "030000"):
                    return doc["docID"]
        except Exception:
            pass
        time.sleep(0.1)
    return None

def get_risk(doc_id):
    r = requests.get(BASE_URL + "/documents/" + doc_id,
        params={"type": 2, "Subscription-Key": EDINET_API_KEY}, timeout=90)
    if r.status_code != 200:
        return "ERROR: HTTP " + str(r.status_code)
    pdf_bytes = r.content
    pages = []
    in_risk = False
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if "事業等のリスク" in text:
                in_risk = True
            if in_risk:
                pages.append(text)
            if in_risk and "経営者による財政状態" in text:
                break
    return "\n".join(pages) if pages else "セクション見つからず"

def run(name):
    if name not in CACHE:
        return {"error": name + " はキャッシュにありません。トヨタ自動車・メルカリ・HODL1 をお試しください。"}
    code, sec, doc_id = CACHE[name]
    if not doc_id:
        doc_id = get_doc_id(code)
    if not doc_id:
        return {"error": "docID取得失敗"}
    return {"company": name, "edinet_code": code, "sec_code": sec,
            "doc_id": doc_id, "risk_text": get_risk(doc_id)}

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "トヨタ自動車"
    print(json.dumps(run(name), ensure_ascii=False, indent=2))
