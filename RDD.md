# 要件定義書（RDD）v2.0
## LegalDD Agent — 上場企業法的リスクDD自動生成エージェント

**バージョン**: 2.0  
**作成日**: 2026年5月2日  
**ハッカソン**: Clawathon Tokyo Edition（Next AI Leaders）  
**対象賞**: ISEAI賞（100,000円）、Grand Prize（125,000円）

---

## 1. プロジェクト概要

### 1.1 プロダクト名
**LegalDD Agent**

### 1.2 一文説明
上場企業名をDiscordに入力するだけで、EDINET API経由で有価証券報告書を直接取得し、金商法・開示府令が要求する開示項目に基づいた**法的リスクDDレポートを自動生成する**AIエージェント。

### 1.3 背景・課題
M&A・投資・法務レビューにおいて、対象企業の法的リスク初期スクリーニングには、弁護士やアナリストが複数の開示書類を横断的に読解する必要がある。このプロセスは定型性が高く、AIエージェントによる自動化に適している。

既存のLegalAI製品はドキュメント貼り付け型（A-2型）が主流であり、**企業名のみから官公庁公式データベース（EDINET）を自律的に取得・構造化するA-1型**の空白が存在する。

### 1.4 差別化軸

| 軸 | 内容 |
|----|------|
| データソースの正確性 | Web検索ではなくEDINET API（金融庁公式）から有価証券報告書原文を直接取得 |
| 法令根拠の明示 | 金商法第24条・開示府令第二号様式の開示項目をDDフレームとして使用 |
| 操作の簡便性 | ISEAI（OpenClaw）＋Discord連携で企業名のみを入力するだけ |
| 拡張設計 | Phase 1（法的リスク）→ Phase 2（財務・ガバナンス等全項目）の明確なロードマップ |

---

## 2. スコープ定義

### 2.1 フェーズ構成

```
Phase 1（本ハッカソン MVP）
  入力: A-1型 — 企業名のみ
  情報源: EDINET API v2（有価証券報告書 PDF）
  出力: 法的リスク8カテゴリDDレポート
  チャネル: Discord

Phase 2（ハッカソン後）
  入力: A-2型 追加 — 文書テキスト貼り付けも受理
  情報源: EDINET API XBRL/CSV（type=5）による財務構造化データ
  出力: 財務・ガバナンス等の全項目DDに拡張
```

### 2.2 対象企業
東京証券取引所上場企業（EDINETに有価証券報告書が提出されているすべての企業）

---

## 3. 機能要件

### 3.1 Discordコマンド仕様

```
/dd [企業名]
```

**例:**
```
/dd トヨタ自動車
/dd 株式会社メルカリ
/dd HODL1
```

**オプション:**
```
/dd [企業名] --type legal     # 法的リスクのみ（デフォルト）
/dd help                      # コマンドヘルプ表示
```

**設計方針:**
- 自然文（「〇〇の法的リスクを調べて」）でも同等に動作する
- EDINETに企業が見つからない場合は、その旨をDiscordに返答する
- 処理中は進捗メッセージを返す（「取得中...」「分析中...」）

### 3.2 エージェント処理フロー

```
[Discord] /dd [企業名]
    │
    ▼
[Step 1] 企業特定
  EDINETコードリスト（CSV）を参照し
  企業名からEDINETコード（Exxxxx）を取得
    │
    ▼
[Step 2] docID取得（書類一覧API）
  GET https://api.edinet-fsa.go.jp/api/v2/documents.json
    ?date={直近営業日}
    &type=2
    &Subscription-Key={EDINET_API_KEY}
  → ordinanceCode="010" & formCode="030000" でフィルタ
  → 対象企業の最新有価証券報告書 docID を取得
    │
    ▼
[Step 3] 書類取得（書類取得API）
  GET https://api.edinet-fsa.go.jp/api/v2/documents/{docID}
    ?type=2
    &Subscription-Key={EDINET_API_KEY}
  → ZIP → PDF 抽出
  → pdfplumber で「事業等のリスク」セクション抽出
    │
    ▼
[Step 4] 法的リスク分析
  抽出テキストを8カテゴリに分類
  各カテゴリの重要度（High/Medium/Low）評価
    │
    ▼
[Step 5] レポート生成・Discord出力
  Markdownフォーマットで出力
  情報源URL・免責事項を付記
```

### 3.3 非機能要件

| 項目 | 要件 |
|------|------|
| レスポンス時間 | コマンド入力から初期応答まで60秒以内 |
| 出力言語 | 日本語 |
| データソース | EDINET API v2（有価証券報告書 type=2） |
| 免責事項 | レポート末尾に法的アドバイスでない旨を必ず明記 |
| エラー処理 | 企業特定失敗・API失敗時にDiscordへ通知 |

---

## 4. 出力仕様

### 4.1 法的リスクDDレポートの構成（Phase 1 MVP）

金商法第24条・開示府令第二号様式「事業等のリスク」の開示要求項目に基づき、以下の8カテゴリを標準DDフレームとして定義する。株式会社HODL1（E05320、2026年4月30日提出の有価証券届出書）を参照例として一般要素を抽出している。

#### DDカテゴリ定義

| # | カテゴリ | 開示根拠 | 主な確認項目 |
|---|---------|---------|------------|
| 1 | 継続企業前提（GCリスク） | 開示府令第二号様式・監査基準委員会報告書570 | GC注記の有無、過去3期の損益トレンド、GC疑義記載 |
| 2 | 訴訟・法的紛争 | 開示府令第二号様式「事業等のリスク」 | 係争訴訟の概要・請求額、行政処分・課徴金の有無、訴訟費用の業績影響 |
| 3 | 規制・ライセンス | 開示府令第二号様式「事業等のリスク」 | 許認可・登録の状況、規制変更リスク、業界固有の規制環境 |
| 4 | コンプライアンス・不正 | 開示府令第二号様式・CGレポート | 不祥事・不正経理の有無、内部通報制度の整備、反社会的勢力排除の確認 |
| 5 | ガバナンス | 開示府令第二号様式・CGレポート（東証要請） | 取締役会の独立性、経営陣の急激な交代・役員訴訟、支配株主との利益相反 |
| 6 | 重要契約 | 開示府令第二号様式「重要な契約等」 | 主要契約の集中・依存度、解除条件・CoC条項、関連当事者取引 |
| 7 | 知的財産・情報セキュリティ | 開示府令第二号様式「事業等のリスク」 | 特許・商標の侵害リスク、個人情報保護法対応、サイバーインシデントの有無 |
| 8 | 財務・資金調達（法的側面） | 開示府令第二号様式「事業等のリスク」 | 財務制限条項（コベナンツ）、第三者割当の相当性、希薄化開示 |

### 4.2 Discord出力フォーマット

```markdown
## 📋 LegalDD Report — [企業名]（証券コード: XXXX）
**分析日時**: YYYY年MM月DD日 HH:MM
**データソース**: EDINET 有価証券報告書（docID: XXXXXXXX）

---

### 総合評価サマリー
| カテゴリ | リスク評価 | 概要 |
|---------|-----------|------|
| 継続企業前提 | 🔴 High | GC重要事象の記載あり |
| 訴訟・法的紛争 | 🔴 High | 総額33億円の訴訟が係属中 |
| 規制・ライセンス | 🟡 Medium | 暗号資産交換業の規制変更リスク |
| コンプライアンス | 🔴 High | 旧経営陣による不正行為が調査報告書で認定 |
| ガバナンス | 🔴 High | 2025年に経営陣が全面交代、取締役会の形骸化が確認 |
| 重要契約 | 🟡 Medium | 代物弁済関連の複数契約が存在 |
| 知的財産・情報セキュリティ | 🟢 Low | 特段のリスク記載なし |
| 財務・資金調達（法的） | 🔴 High | 第三者割当新株予約権による希薄化リスク |

---

### 詳細分析

#### 1. 継続企業前提（GCリスク）🔴 High
[EDINET原文から抽出した根拠を3〜5行で記述]

#### 2. 訴訟・法的紛争 🔴 High
[EDINET原文から抽出した根拠を3〜5行で記述]

（以下、各カテゴリ）

---

### データソース
- EDINET: https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?...
- 書類: 有価証券報告書（第30期、2025年10月期）

---
⚠️ 本レポートはAIによるEDINET公開情報の自動分析です。
法的アドバイスではありません。投資・法務判断は専門家にご相談ください。
```

---

## 5. 技術設計

### 5.1 システム構成

```
[Discord] ───────────────────────────────────────────────┐
    │                                                    │
    ▼                                                    │
[ISEAI Gateway]                                          │
  (OpenClaw on Alibaba Cloud)                            │
    │                                                    │
    ├──[万能アシスタント]──────────────────────────────────┤
    │     企業名の解釈、分析ロジック                        │
    │                                                    │
    ├──[プログラミングエージェント]────────────────────────┤
    │     edinet_fetcher.py の実行                        │
    │     EDINET API呼び出し・PDF解析                     │
    │                                                    │
    └──[オフィスアシスタント]──────────────────────────────┘
          Markdownレポートのフォーマット整形

[外部API]
  ├── EDINET API v2（金融庁）
  │     https://api.edinet-fsa.go.jp/api/v2/
  └── EDINETコードリストCSV（金融庁公開）
        https://disclosure2dl.edinet-fsa.go.jp/...
```

### 5.2 EDINET API v2 仕様詳細

#### エンドポイント一覧

| API | エンドポイント | 用途 |
|-----|--------------|------|
| 書類一覧API | `GET /api/v2/documents.json` | 日付・書類種別でdocID一覧取得 |
| 書類取得API | `GET /api/v2/documents/{docID}` | 書類本体のZIPダウンロード |

#### 書類種別コード（本プロジェクト使用分）

| ordinanceCode | formCode | 書類種類 |
|--------------|----------|---------|
| 010 | 030000 | 有価証券報告書 |
| 010 | 030001 | 訂正有価証券報告書 |
| 010 | 050000 | 有価証券届出書（通常方式） |

#### typeパラメータ（書類取得API）

| type値 | 内容 | Phase 1での用途 |
|--------|------|---------------|
| 2 | PDF | メイン（事業等のリスク抽出） |
| 5 | XBRL/CSV | Phase 2（財務構造化データ） |

#### 認証

```
Subscription-Key: {EDINET_API_KEY}
※ 環境変数 EDINET_API_KEY に設定
```

### 5.3 edinet_fetcher.py 設計

```python
"""
edinet_fetcher.py
EDINET API v2 を使用して有価証券報告書の「事業等のリスク」セクションを取得する。
"""
import requests, zipfile, io, os, json, sys, time
from datetime import datetime, timedelta
import pdfplumber

EDINET_API_KEY = os.environ.get("EDINET_API_KEY", "")
BASE_URL = "https://api.edinet-fsa.go.jp/api/v2"

# ------------------------------------------------------------------
# Step 1: 企業名 → EDINETコード
# ------------------------------------------------------------------
def resolve_edinet_code(company_name: str) -> str | None:
    """
    EDINETコードリストCSVから企業名でEDINETコードを検索する。
    完全一致 → 部分一致の順でフォールバック。
    """
    url = ("https://disclosure2dl.edinet-fsa.go.jp/guide/static/"
           "disclosure/download/EKW0EAP0015.zip")
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        return None
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        csv_file = [f for f in z.namelist() if f.endswith(".csv")][0]
        content = z.read(csv_file).decode("cp932", errors="replace")
    # CSVをパースしてEDINETコードを検索
    for line in content.splitlines():
        cols = line.split(",")
        if len(cols) < 6:
            continue
        edinet_code = cols[0].strip().strip('"')
        name = cols[2].strip().strip('"')   # 提出者名
        if company_name in name or name in company_name:
            return edinet_code
    return None

# ------------------------------------------------------------------
# Step 2: EDINETコード → 最新有価証券報告書 docID
# ------------------------------------------------------------------
def get_latest_doc_id(edinet_code: str) -> tuple[str | None, str | None]:
    """
    直近365日を遡って最新の有価証券報告書docIDを返す。
    Returns: (docID, submitDateTime)
    """
    for delta in range(0, 365):
        date = (datetime.today() - timedelta(days=delta)).strftime("%Y-%m-%d")
        try:
            resp = requests.get(
                f"{BASE_URL}/documents.json",
                params={"date": date, "type": 2,
                        "Subscription-Key": EDINET_API_KEY},
                timeout=10
            )
            if resp.status_code != 200:
                continue
            for doc in resp.json().get("results", []):
                if (doc.get("edinetCode") == edinet_code
                        and doc.get("ordinanceCode") == "010"
                        and doc.get("formCode") == "030000"):
                    return doc["docID"], doc.get("submitDateTime", "")
            time.sleep(0.3)   # APIレート制限対応
        except Exception:
            continue
    return None, None

# ------------------------------------------------------------------
# Step 3: docID → 事業等のリスク テキスト抽出
# ------------------------------------------------------------------
def fetch_risk_section(doc_id: str) -> str:
    """
    EDINET から有価証券報告書PDFを取得し「事業等のリスク」セクションを抽出。
    """
    resp = requests.get(
        f"{BASE_URL}/documents/{doc_id}",
        params={"type": 2, "Subscription-Key": EDINET_API_KEY},
        timeout=60
    )
    if resp.status_code != 200:
        return f"[ERROR] 書類取得失敗: HTTP {resp.status_code}"
    # ZIP → PDF 取得
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        pdf_files = [
            f for f in z.namelist()
            if f.endswith(".pdf") and "AuditDoc" not in f
        ]
        if not pdf_files:
            return "[ERROR] PDFファイルが見つかりませんでした"
        pdf_bytes = z.read(pdf_files[0])
    # pdfplumber でセクション抽出
    risk_pages = []
    in_risk = False
    RISK_START = "事業等のリスク"
    RISK_END   = "経営者による財政状態"
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if RISK_START in text:
                in_risk = True
            if in_risk:
                risk_pages.append(text)
            if in_risk and RISK_END in text:
                break
    return "\n".join(risk_pages) if risk_pages else "[INFO] リスクセクションが見つかりませんでした"

# ------------------------------------------------------------------
# メインエントリポイント
# ------------------------------------------------------------------
def run(company_name: str) -> dict:
    result = {"company": company_name, "edinet_code": None,
              "doc_id": None, "submit_date": None, "risk_text": ""}
    edinet_code = resolve_edinet_code(company_name)
    if not edinet_code:
        result["error"] = f"企業 '{company_name}' がEDINETコードリストに見つかりませんでした"
        return result
    result["edinet_code"] = edinet_code
    doc_id, submit_date = get_latest_doc_id(edinet_code)
    if not doc_id:
        result["error"] = "有価証券報告書が見つかりませんでした（過去365日分を検索）"
        return result
    result["doc_id"] = doc_id
    result["submit_date"] = submit_date
    result["risk_text"] = fetch_risk_section(doc_id)
    return result

if __name__ == "__main__":
    company = sys.argv[1] if len(sys.argv) > 1 else "トヨタ自動車"
    output = run(company)
    print(json.dumps(output, ensure_ascii=False, indent=2))
```

### 5.4 プロンプト設計（SOUL.md）

```markdown
# LegalDD Agent

## 役割
あなたはLegalDDという名前の法的リスク分析エージェントです。
上場企業名をDiscordで受け取り、EDINET APIから有価証券報告書を
直接取得・分析し、金商法・開示府令に基づく法的リスクDDレポートを生成します。

## /dd コマンドの処理手順

1. edinet_fetcher.py を実行して有価証券報告書の「事業等のリスク」テキストを取得
   ```
   python edinet_fetcher.py "[企業名]"
   ```

2. 取得したテキストを以下の8カテゴリで分析する：
   - 継続企業前提（GCリスク）
   - 訴訟・法的紛争
   - 規制・ライセンス
   - コンプライアンス・不正
   - ガバナンス
   - 重要契約
   - 知的財産・情報セキュリティ
   - 財務・資金調達（法的側面）

3. 各カテゴリにリスク評価（🔴High / 🟡Medium / 🟢Low）を付与する。
   評価基準：
   - High: 業績・事業継続に重大な影響を与えうるリスクが明記されている
   - Medium: リスクは存在するが現時点で限定的・管理されている
   - Low: 顕著なリスクの記載がない、または一般的な開示水準

4. 指定のMarkdownフォーマットでDiscordに出力する

## 禁止事項
- 投資推奨・売買推奨の記載
- 確認できていない事実の断定的記載
- 出典のない評価

## 必須付記
レポートの末尾に必ず以下を記載：
「⚠️ 本レポートはAIによるEDINET公開情報の自動分析です。
法的アドバイスではありません。投資・法務判断は専門家にご相談ください。」
```

### 5.5 ISEAIセットアップ手順

#### 環境変数設定
ISEAIダッシュボード → 設定 → 環境変数に以下を追加：
```
EDINET_API_KEY=取得したSubscription-Key
```

#### Skillの配置
1. ISEAIのWorkspaceに`edinet_fetcher.py`を配置
2. 依存ライブラリのインストール確認：`requests`, `pdfplumber`

#### Discord連携設定
1. Discord Developer Portal → New Application → Bot作成
2. Bot Token取得 → ISEAIのDiscord設定画面に貼り付け
3. OAuth2 URLでBotをサーバーに招待
4. テストDM送信でペアリング確認

---

## 6. 拡張ロードマップ

### Phase 1（本ハッカソン MVP）
- A-1型：企業名 → EDINET API → 法的リスク8カテゴリDDレポート
- Discord連携

### Phase 2（ハッカソン後）

**A-2型の追加:**
```
/dd upload [企業名]
→ エージェントが文書テキストの貼り付けを待機
→ EDINET取得データと組み合わせた高精度分析
```

**XBRL/CSVによる財務データ統合（type=5）:**
- `jpcorp_cor:NetSalesSummary` 等のXBRL要素を直接パース
- 財務指標の5期トレンド分析
- 売上・利益・CF・純資産の推移グラフ化

**出力カテゴリ拡張:**

| 追加カテゴリ | EDINETの対応開示項目 |
|------------|-------------------|
| 財務状況 | 主要な経営指標等の推移 |
| 事業環境リスク | 市場・競合・技術変化 |
| ガバナンス詳細 | コーポレートガバナンス報告書 |
| 株主・支配権 | 大株主状況・支配株主との利益相反 |
| サステナビリティ | ESG・気候変動リスク開示 |

### Phase 3（将来構想）
- 定期モニタリング（適時開示を検知して自動アラート）
- 複数企業の横断比較分析
- TDnetリアルタイム連携

---

## 7. GitHub提出物仕様

### 7.1 リポジトリ構成

```
legaldd-agent/
├── README.md                    # プロジェクト概要・デモ・セットアップ手順
├── SOUL.md                      # エージェント人格・行動指針
├── AGENTS.md                    # マルチエージェント設定
├── scripts/
│   ├── edinet_fetcher.py        # EDINET API呼び出し・PDF解析コア
│   └── requirements.txt         # 依存ライブラリ（requests, pdfplumber）
├── prompts/
│   ├── system_prompt.md         # メインシステムプロンプト
│   ├── legal_risk_v1.md         # Phase 1 法的リスク分析プロンプト
│   └── full_dd_v1.md            # Phase 2 全項目DD（Placeholder）
├── examples/
│   ├── demo_input.md            # デモ用入力サンプル（複数企業）
│   └── demo_output.md           # デモ用出力サンプル（実際の生成結果）
└── docs/
    ├── architecture.md          # システムアーキテクチャ図
    ├── legal_basis.md           # 金商法・開示府令の法的根拠整理
    ├── dd_categories.md         # DDカテゴリ定義と根拠
    └── roadmap.md               # Phase 1〜3ロードマップ
```

### 7.2 Gitコミット計画（開発の軌跡 30%対策）

```
commit 1  [〜12:30]  init: project structure and README skeleton
commit 2  [〜13:00]  feat: add SOUL.md and agent configuration
commit 3  [〜13:30]  feat: add edinet_fetcher.py core script
commit 4  [〜14:00]  feat: add legal risk prompt template
commit 5  [〜15:30]  fix: refine prompt based on first EDINET test
commit 6  [〜16:30]  test: add demo output for HODL1 and second company
commit 7  [〜17:00]  docs: add architecture diagram and legal basis
commit 8  [〜17:30]  feat: add Discord command documentation
commit 9  [〜18:00]  chore: finalize README and submission materials
```

### 7.3 Akindo提出内容
1. プロダクト名：LegalDD Agent
2. 対象スポンサー賞：ISEAI賞
3. GitHubリポジトリURL
4. デモ動画またはスクリーンショット（Discord操作シーン）
5. ISEAIの使用箇所の明示
6. 技術スタック：ISEAI（OpenClaw / Alibaba Cloud）+ Discord + EDINET API v2

---

## 8. デモシナリオ（18:10提出締切向け）

### 8.1 デモフロー（発表3分想定）

**Step 1** DiscordにLegalDD Botが参加している状態を見せる

**Step 2** ライブ入力：
```
/dd 株式会社HODL1
```
→ 「EDINET から有価証券報告書を取得中...」と表示
→ 30〜60秒後にレポート出力

**Step 3** 別企業で比較：
```
/dd トヨタ自動車
```
→ リスクが少ないケースとの対比を示す

**Step 4** プレゼンの軸：
- 「企業名だけで、EDINET公式データから法的リスクが構造化される」
- 「金商法・開示府令という法令根拠に基づいたDDフレーム」
- 「MHMでのIPO・M&A実務への直接応用可能性」
- Phase 2/3のロードマップ

### 8.2 バックアップ対応
EDINET APIの応答遅延に備えて、事前に2〜3社分の出力サンプルを`examples/demo_output.md`に保存しておき、ライブ失敗時にはそちらを提示する。

---

## 9. 制約・リスク

### 9.1 技術的制約

| 制約 | 内容 | 対応 |
|------|------|------|
| ISEAIのPython実行可否 | ワークショップ（12:00）で確認 | 不可の場合はWeb Fetch方式にフォールバック |
| EDINET APIレート制限 | 日次上限あり（詳細未確定） | time.sleep(0.3)でスロットリング対応 |
| PDF解析精度 | pdfplumberで全文取得は確実だがセクション境界の検出精度に依存 | 手動サンプルで事前確認 |
| レスポンス時間 | PDF取得・解析で60秒超の可能性 | 進捗メッセージで対応 |

### 9.2 法的留意事項
- 出力は法的アドバイスでない旨を必ず明記
- 投資判断への使用を推奨しない旨を明記
- 生成AIの出力には誤情報が含まれる可能性を明記

---

## 10. 免責事項

本プロダクトが生成するレポートは、AIによるEDINET公開情報の自動分析であり、法的アドバイス、投資推奨、その他の専門的助言を構成するものではありません。法務・投資に関する最終的な判断は、資格を有する専門家にご相談ください。

