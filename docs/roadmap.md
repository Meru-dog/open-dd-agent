# ロードマップ

## Phase 1 — MVP（Clawathon Tokyo Edition 2026年5月2日）

**目標**: 企業名入力だけで法的リスクDDレポートを生成する

| 機能 | 状態 |
|------|------|
| EDINET API v2 連携（書類一覧・書類取得） | ✅ 実装済み |
| 有価証券報告書 PDF解析（pdfplumber） | ✅ 実装済み |
| 法的リスク8カテゴリ分析 | ✅ 実装済み |
| Discord コマンド連携（/dd） | ✅ 実装済み |
| ISEAI（OpenClaw）上でのデプロイ | ✅ 実装済み |
| A-1型入力（企業名のみ） | ✅ 実装済み |

---

## Phase 2 — 拡張版（2026年Q3予定）

**目標**: 全項目DDへの拡張とA-2型入力の追加

| 機能 | 状態 |
|------|------|
| A-2型入力（文書テキスト貼り付け） | 🔲 予定 |
| XBRL/CSV（type=5）による財務構造化データ取得 | 🔲 予定 |
| 財務・ガバナンス等の追加6カテゴリ | 🔲 予定 |
| 5期分の財務トレンド表示 | 🔲 予定 |
| 複数企業の横断比較（/dd compare [A] [B]） | 🔲 予定 |

---

## Phase 3 — プロダクト化（2026年Q4以降）

**目標**: 継続的なモニタリングとエンタープライズ対応

| 機能 | 状態 |
|------|------|
| 適時開示（TDnet）のリアルタイムモニタリング | 🔲 構想中 |
| 訴訟・行政処分の変更を自動検知してアラート | 🔲 構想中 |
| 定期レポートの自動生成（週次・月次） | 🔲 構想中 |
| API提供（法律事務所・証券会社向け） | 🔲 構想中 |
| ISEAI を超えた自前 OpenClaw デプロイ | 🔲 構想中 |

---

## 想定ユーザー

| フェーズ | 主な利用者 | ユースケース |
|---------|-----------|------------|
| Phase 1 | 弁護士・法務担当者 | M&A・投資案件の法的リスク初期スクリーニング |
| Phase 2 | 証券アナリスト・投資家 | 投資先の包括的DD |
| Phase 3 | 法律事務所・金融機関 | 継続的なポートフォリオ監視 |

---

## 技術的な拡張ポイント

### EDINET XBRL タクソノミー（Phase 2）

```python
# Phase 2 で取得予定の主要財務要素
FINANCIAL_ELEMENTS = {
    "売上高":        "jpcorp_cor:NetSalesSummaryOfBusinessResults",
    "経常損益":      "jpcorp_cor:OrdinaryIncomeLossSummaryOfBusinessResults",
    "当期純損益":    "jpcorp_cor:ProfitLossAttributableToOwnersOfParent",
    "包括利益":      "jpcorp_cor:ComprehensiveIncomeSummaryOfBusinessResults",
    "純資産":        "jpcorp_cor:NetAssetsSummaryOfBusinessResults",
    "総資産":        "jpcorp_cor:TotalAssetsSummaryOfBusinessResults",
    "営業CF":        "jpcorp_cor:CashFlowsFromOperatingActivities",
}
```
