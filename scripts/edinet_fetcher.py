import io, json, os, sys, time, zipfile
from datetime import datetime, timedelta
import requests
import pdfplumber

EDINET_API_KEY = os.environ.get("EDINET_API_KEY", "")
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"

def resolve_edinet_code(company_name):
    sys.stderr.write("[INFO] 企業検索中: " + company_name + "\n")
    for delta in range(0, 400):
        date_str = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            resp = requests.get(BASE_URL + "/documents.json",
                params={"date": date_str, "type": 2, "Subscription-Key": EDINET_API_KEY},
                timeout=10)
            if resp.status_code != 200:
                time.sleep(0.2)
                continue
            for doc in resp.json().get("results", []):
                name = doc.get("filerName", "")
                code = doc.get("edinetCode", "")
                sec  = doc.get("secCode", "")
                if not code:
                    continue
                if company_name in name or name in company_name:
                    sys.stderr.write("[INFO] 発見: " + name + " (" + code + ")\n")
                    return code, sec
        except Exception:
            pass
        time.sleep(0.2)
    return None, None

def get_latest_doc_id(edinet_code):
    sys.stderr.write("[INFO] 有価証券報告書検索中: " + edinet_code + "\n")
    for delta in range(400):
        date_str = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            resp = requests.get(BASE_URL + "/documents.json",
                params={"date": date_str, "type": 2, "Subscription-Key": EDINET_API_KEY},
                timeout=10)
            if resp.status_code != 200:
                time.sleep(0.2)
                continue
            for doc in resp.json().get("results", []):
                if (doc.get("edinetCode") == edinet_code
                        and doc.get("ordinanceCode") == "010"
                        and doc.get("formCode") == "030000"):
                    return doc["docID"], doc.get("submitDateTime", "")
        except Exception:
            pass
        time.sleep(0.2)
    return None, None

def fetch_risk_section(doc_id):
    sys.stderr.write("[INFO] PDF取得中: " + doc_id + "\n")
    # type=2 は直接PDFを返す（ZIPではない）
    resp = requests.get(BASE_URL + "/documents/" + doc_id,
        params={"type": 2, "Subscription-Key": EDINET_API_KEY}, timeout=90)
    if resp.status_code != 200:
        return "[ERROR] HTTP " + str(resp.status_code)

    # Content-Typeを確認してPDF/ZIP両対応
    content_type = resp.headers.get("Content-Type", "")
    sys.stderr.write("[INFO] Content-Type: " + content_type + "\n")

    pdf_bytes = None

    if "zip" in content_type or resp.content[:2] == b'PK':
        # ZIPの場合
        try:
            with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                pdfs = [f for f in z.namelist()
                        if f.lower().endswith(".pdf") and "audit" not in f.lower()]
                if pdfs:
                    pdf_bytes = z.read(max(pdfs, key=lambda f: z.getinfo(f).file_size))
        except Exception as e:
            return "[ERROR] ZIP解析失敗: " + str(e)
    elif "pdf" in content_type or resp.content[:4] == b'%PDF':
        # 直接PDFの場合
        pdf_bytes = resp.content
    else:
        return "[ERROR] 不明なContent-Type: " + content_type

    if not pdf_bytes:
        return "[ERROR] PDFバイトが空"

    # pdfplumberでリスクセクション抽出
    pages = []
    in_risk = False
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            sys.stderr.write("[INFO] 総ページ数: " + str(len(pdf.pages)) + "\n")
            for page in pdf.pages:
                text = page.extract_text() or ""
                if "事業等のリスク" in text:
                    in_risk = True
                if in_risk:
                    pages.append(text)
                if in_risk and "経営者による財政状態" in text:
                    break
    except Exception as e:
        return "[ERROR] PDF解析失敗: " + str(e)

    if not pages:
        return "[INFO] セクション見つからず"
    return "\n".join(pages)

def run(company_name):
    result = {
        "company": company_name,
        "edinet_code": None,
        "sec_code": None,
        "doc_id": None,
        "submit_date": None,
        "risk_text": ""
    }
    code, sec = resolve_edinet_code(company_name)
    if not code:
        result["error"] = "'" + company_name + "' がEDINETに見つかりません"
        return result
    result["edinet_code"] = code
    result["sec_code"] = sec
    doc_id, submit_date = get_latest_doc_id(code)
    if not doc_id:
        result["error"] = "有価証券報告書が見つかりません"
        return result
    result["doc_id"] = doc_id
    result["submit_date"] = submit_date
    result["risk_text"] = fetch_risk_section(doc_id)
    return result

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "トヨタ自動車"
    print(json.dumps(run(company), ensure_ascii=False, indent=2))
