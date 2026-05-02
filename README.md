# open-dd-agent 🔍

**企業名を入力するだけで、EDINET公式データから法的リスクDDレポートを自動生成するAIエージェント**

[![Built with OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-red?style=flat-square)](https://openclaw.ai)
[![Powered by ISEAI](https://img.shields.io/badge/Powered%20by-ISEAI-blue?style=flat-square)](https://iseai.jp)
[![Data Source](https://img.shields.io/badge/Data-EDINET%20API%20v2-green?style=flat-square)](https://disclosure.edinet-fsa.go.jp)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## 概要

`open-dd-agent` は、上場企業の法的リスクデューデリジェンス（DD）を自動化するAIエージェントです。

Discordに企業名を送るだけで、金融庁の公式データベース **EDINET API v2** から有価証券報告書を直接取得・解析し、**金融商品取引法（金商法）・企業内容等の開示に関する内閣府令（開示府令）** が求める開示項目に基づいた法的リスクレポートを生成します。

```
Discord: /dd トヨタ自動車

→ EDINET から有価証券報告書を取得中... (docID: S100XXXX)
→ 事業等のリスクセクションを解析中...
→ 📋 LegalDD Report — トヨタ自動車株式会社（7203）
   ...
```

---

## デモ

> **Clawathon Tokyo Edition（2026年5月2日）提出プロダクト**

| コマンド | 説明 |
|---------|------|
| `/dd [企業名]` | 法的リスクDDレポートを生成 |
| `/dd [企業名] --type legal` | 法的リスクのみ（デフォルト） |
| `/dd help` | ヘルプ表示 |

### サンプル出力

```markdown
## 📋 LegalDD Report — 株式会社HODL1（3719）
**分析日時**: 2026年5月2日 15:32
**データソース**: EDINET 有価証券報告書（第30期、docID: S100XXXXX）

### 総合評価サマリー
| カテゴリ              | リスク評価  | 概要                               |
|--------------------|-----------|----------------------------------|
| 継続企業前提          | 🔴 High   | GC重要事象の記載あり                  |
| 訴訟・法的紛争         | 🔴 High   | 総額33億円超の訴訟が係属中              |
| 規制・ライセンス        | 🟡 Medium | 暗号資産交換業の規制変更リスク            |
| コンプライアンス・不正   | 🔴 High   | 旧経営陣による不正行為が調査報告書で認定    |
| ガバナンス            | 🔴 High   | 2025年に経営陣が全面交代               |
| 重要契約              | 🟡 Medium | 代物弁済関連の複数契約が存在             |
| 知的財産・情報セキュリティ | 🟢 Low   | 特段のリスク記載なし                   |
| 財務・資金調達（法的）   | 🔴 High   | 第三者割当新株予約権による希薄化リスク      |

⚠️ 本レポートはAIによるEDINET公開情報の自動分析です。
法的アドバイスではありません。投資・法務判断は専門家にご相談ください。
```

---

## アーキテクチャ

```
Discord
   │  /dd [企業名]
   ▼
ISEAI Gateway（OpenClaw on Alibaba Cloud）
   │
   ├─ [万能アシスタント]       企業名の解釈・法的リスク分析
   ├─ [プログラミングエージェント]  edinet_fetcher.py の実行
   └─ [オフィスアシスタント]    Markdownレポートの整形・出力
          │
          ▼
   EDINET API v2（金融庁）
   https://api.edinet-fsa.go.jp/api/v2/
   │
   ├─ 書類一覧API  → 最新有価証券報告書の docID 取得
   └─ 書類取得API  → PDF 取得 → 事業等のリスクセクション抽出
```

---

## 法的根拠

本プロダクトのDDフレームは以下の法令・基準に基づいています。

| 法令・基準 | 参照箇所 | DDフレームへの対応 |
|----------|---------|-----------------|
| 金融商品取引法（金商法）第24条 | 有価証券報告書の提出義務 | 対象書類の選定根拠 |
| 企業内容等の開示に関する内閣府令（開示府令）第二号様式 | 「事業等のリスク」開示要求 | 8カテゴリDDフレームの設計根拠 |
| 企業内容等の開示に関する内閣府令（開示府令）第二号様式 | 「重要な契約等」開示要求 | カテゴリ6（重要契約リスク）の根拠 |
| 監査基準委員会報告書570 | 継続企業の前提 | カテゴリ1（GCリスク）の根拠 |

---

## 法的リスクDDカテゴリ（Phase 1 MVP）

金商法・開示府令が要求する「事業等のリスク」の一般的な開示要素として、以下の8カテゴリを定義しています。

| # | カテゴリ | 主な確認項目 |
|---|---------|------------|
| 1 | **継続企業前提（GCリスク）** | GC注記の有無、過去3期の損益トレンド、GC疑義の記載 |
| 2 | **訴訟・法的紛争** | 係争訴訟の概要・請求額、行政処分・課徴金の有無 |
| 3 | **規制・ライセンス** | 必要な許認可・登録の状況、業法改正リスク |
| 4 | **コンプライアンス・不正** | 不祥事・不正経理の有無、内部通報制度の整備状況 |
| 5 | **ガバナンス** | 取締役会の独立性、経営陣の急激な交代・役員訴訟 |
| 6 | **重要契約** | 主要契約の集中・依存度、CoC条項、関連当事者取引 |
| 7 | **知的財産・情報セキュリティ** | 特許・商標の侵害リスク、サイバーインシデントの有無 |
| 8 | **財務・資金調達（法的側面）** | 財務制限条項、第三者割当の相当性、希薄化開示 |

---

## セットアップ

### 前提条件

- [ISEAI](https://iseai.jp/) アカウント（OpenClaw マネージドサービス）
- Discord アカウント・サーバー
- [EDINET API v2](https://api.edinet-fsa.go.jp/) の Subscription-Key

### 1. EDINET API キーの取得

[EDINET API 申請ページ](https://api.edinet-fsa.go.jp/api/auth/index.aspx?mode=1) でメールアドレスのみで即時発行されます。

### 2. ISEAI の設定

1. [ISEAI](https://iseai.jp/) にサインインし、ワークスペースを開く
2. 環境変数に `EDINET_API_KEY` を追加
3. `scripts/edinet_fetcher.py` をワークスペースに配置
4. `SOUL.md` の内容をエージェント設定に貼り付け

### 3. Discord Bot の設定

1. [Discord Developer Portal](https://discord.com/developers/applications) で新規アプリケーションを作成
2. Bot タブで Token を発行
3. ISEAI の Discord 設定画面に Token を貼り付け
4. OAuth2 URL Generator で Bot をサーバーに招待
5. Discord の DM で `hello` を送信してペアリングを確認

### 4. 動作確認

Discord で以下を実行して動作を確認します：

```
/dd トヨタ自動車
```

---

## ファイル構成

```
open-dd-agent/
├── README.md                    # このファイル
├── SOUL.md                      # エージェント人格・行動指針
├── AGENTS.md                    # マルチエージェント設定
├── scripts/
│   ├── edinet_fetcher.py        # EDINET API呼び出し・PDF解析コア
│   └── requirements.txt         # 依存ライブラリ
├── prompts/
│   ├── system_prompt.md         # メインシステムプロンプト
│   ├── legal_risk_v1.md         # Phase 1 法的リスク分析プロンプト
│   └── full_dd_v1.md            # Phase 2 全項目DD（予定）
├── examples/
│   ├── demo_input.md            # デモ用入力サンプル
│   └── demo_output.md           # デモ用出力サンプル
└── docs/
    ├── architecture.md          # システムアーキテクチャ詳細
    ├── legal_basis.md           # 金商法・開示府令の法的根拠
    ├── dd_categories.md         # DDカテゴリ定義と根拠
    └── roadmap.md               # Phase 1〜3 ロードマップ
```

---

## ロードマップ

```
Phase 1（MVP）  ← 現在
  企業名入力 → EDINET API → 法的リスク8カテゴリDDレポート
  Discord連携

Phase 2（次期開発）
  A-2型追加: 文書テキスト貼り付けによる高精度分析
  XBRL/CSV（type=5）による財務構造化データの統合
  財務・ガバナンス等の全項目DDへ拡張

Phase 3（将来構想）
  適時開示のリアルタイムモニタリング・自動アラート
  複数企業の横断比較分析
  TDnet連携
```

---

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| エージェント基盤 | [ISEAI](https://iseai.jp/)（OpenClaw on Alibaba Cloud） |
| チャネル | Discord |
| データソース | EDINET API v2（金融庁） |
| PDF解析 | pdfplumber |
| 言語 | Python 3.11+ |

---

## 免責事項

本プロダクトが生成するレポートは、AIによるEDINET公開情報の自動分析であり、**法的アドバイス、投資推奨、その他の専門的助言を構成するものではありません**。法務・投資に関する最終的な判断は、資格を有する専門家にご相談ください。

---

## ライセンス

MIT License — 詳細は [LICENSE](LICENSE) を参照してください。
