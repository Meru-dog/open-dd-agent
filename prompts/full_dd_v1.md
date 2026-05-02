# 全項目DDプロンプト v1.0（Phase 2 予定）

> **ステータス**: Phase 2 開発予定。現時点では Placeholder です。

---

## Phase 2 で追加予定のDDカテゴリ

Phase 1（法的リスク8カテゴリ）に加えて、以下を追加します。

| カテゴリ | EDINETの対応開示項目 | データ取得方法 |
|--------|------------------|------------|
| 財務状況 | 主要な経営指標等の推移（売上・利益・CF・純資産） | XBRL/CSV type=5 |
| 事業環境リスク | 市場・競合・技術変化リスク | PDF type=2 |
| ガバナンス詳細 | コーポレートガバナンス報告書 | PDF type=2 |
| 株主・支配権 | 大株主状況・支配株主との利益相反 | PDF type=2 |
| 設備・R&D | 重要設備・研究開発の状況 | PDF type=2 |
| サステナビリティ | ESG・気候変動リスク開示（TCFD準拠） | PDF type=2 |

---

## XBRL/CSV 連携設計（Phase 2）

EDINET API の `type=5` で取得できる XBRL/CSV（EDINETタクソノミー形式）を
直接パースして財務指標を構造化データとして取得します。

```python
# Phase 2 で実装予定の財務データ取得ロジック（概要）

XBRL_ELEMENTS = {
    "売上高":     "jpcorp_cor:NetSalesSummaryOfBusinessResults",
    "経常損益":   "jpcorp_cor:OrdinaryIncomeLossSummaryOfBusinessResults",
    "当期純損益":  "jpcorp_cor:ProfitLossAttributableToOwnersOfParent",
    "純資産":     "jpcorp_cor:NetAssetsSummaryOfBusinessResults",
    "総資産":     "jpcorp_cor:TotalAssetsSummaryOfBusinessResults",
}

# type=5 で取得した ZIP を解凍し、CSV をパースして
# 5期分のトレンドデータを抽出する
```

---

## A-2型入力（Phase 2）

```
/dd upload [企業名]
```

エージェントが文書テキストの貼り付けを待機し、
EDINET取得データと組み合わせた高精度分析を実施します。
