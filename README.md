# Hono Japanese BBQ · 官方網站

7 頁靜態網站（Home／Menu／Drinks／Groups／Visit／About／FAQ），用 Python 產生。
架構參考 Fogo de Chão 分店網站，價格卡參考 Texas de Brazil，價格規則和團體頁參考 Chama Gaúcha，語氣參考 Uchi Dallas。
做法沿用 CarePlus 網站（內容和版型分開、自動檢查、推上 main 就自動發布）。

**完整的逐步操作指南：** `../05-website-build-guide.html`

## 目錄

```
content/facts.py     所有事實：價格、時間、酒單、規則、FAQ 來源、「待確認」清單 ← 最常改的檔案
content/pages.py     每頁的結構和文案
assets/site.css      全站唯一的樣式檔
assets/img/          照片（800／1600 兩種寬度）
build.py             產生器 → dist/
validate.py          檢查：連結、H1、schema、FAQ 一致性、NAP、圖片、JS、表單把關
check_copy.py        文案守門員：Honō／75052／soft opening／best／100% American Wagyu…
serve.py             本機預覽 http://localhost:4174
.github/workflows/deploy.yml   自動建置、檢查、發布
```

## 本機改內容

```bash
python3 build.py && python3 validate.py && python3 check_copy.py
python3 serve.py
```

## 「待確認」怎麼用

沒有來源的說法（停車、包場人數、沙拉吧……）寫在 `content/facts.py` 的 `PENDING`，**不會出現在網站上**。
客人確認後，在 `CONFIRMED` 加一行，例如：

```python
CONFIRMED = {
    "parking": "Owner (Kelly 轉述), 2026-10-28 — free lot",
}
```

重新建置後它就會出現在對應的頁面和 FAQ。內部審稿頁：`/_pending/`（noindex）。

## 建置參數

| 變數 | 用途 | 預設 |
|---|---|---|
| `SITE_URL` | canonical／schema／sitemap 的網域 | `https://example.invalid`（只允許 noindex 時使用） |
| `BASE_PATH` | GitHub Pages 專案子路徑 | 空 |
| `NOINDEX` | `1` 擋 Google（預覽）；`0` 開放收錄 | `1` |
| `GTM_ID` | Google Tag Manager 容器 | 空 |
| `FORM_ACCESS_KEY` | Web3Forms 金鑰（放 repo secret） | 空 |
| `CNAME_DOMAIN` | 自訂網域（正式上線時設定） | 空 |
