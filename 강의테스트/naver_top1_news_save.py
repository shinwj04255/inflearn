import sys
import io
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# ── 1. 코스피 상승 1위 종목 수집 ──────────────────────────────
res = requests.get("https://finance.naver.com/sise/sise_rise.nhn?sosok=0", headers=headers)
res.encoding = "euc-kr"
soup = BeautifulSoup(res.text, "html.parser")

stocks = []
for row in soup.select_one("table.type_2").select("tr"):
    cols = row.select("td")
    if len(cols) < 5:
        continue
    name_tag = cols[1].select_one("a")
    if not name_tag:
        continue
    try:
        name   = name_tag.get_text(strip=True)
        price  = int(cols[2].get_text(strip=True).replace(",", ""))
        rate   = float(cols[4].get_text(strip=True).replace("%", "").replace("+", "").replace(",", ""))
        volume = int(cols[5].get_text(strip=True).replace(",", ""))
    except ValueError:
        continue
    if price >= 1_000 and rate >= 5.0:
        stocks.append({"종목명": name, "현재가": price, "등락률": rate, "거래량": volume})

stocks.sort(key=lambda s: s["등락률"], reverse=True)
top = stocks[0]

print(f"  1위 종목: {top['종목명']}  현재가: {top['현재가']:,}원  등락률: +{top['등락률']}%")

# ── 2. 네이버 뉴스 최신 3건 수집 ─────────────────────────────
news_url = (
    "https://search.naver.com/search.naver"
    f"?where=news&query={requests.utils.quote(top['종목명'])}&sort=1"
)
res = requests.get(news_url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

seen = set()
news_list = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if (
        len(text) > 10
        and href not in seen
        and any(k in href for k in ["article", "news", "idxno", "view"])
        and "help.naver" not in href
        and "news.naver.com/main/static" not in href
    ):
        seen.add(href)
        news_list.append({"제목": text, "링크": href})
    if len(news_list) == 3:
        break

for i, n in enumerate(news_list, 1):
    print(f"  뉴스 {i}: {n['제목'][:50]}")

# ── 3. CSV 저장 ───────────────────────────────────────────────
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename  = f"top1_news_{timestamp}.csv"

with open(filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    # 종목 정보 헤더 + 데이터
    writer.writerow(["[종목 정보]"])
    writer.writerow(["종목명", "현재가(원)", "등락률(%)", "거래량"])
    writer.writerow([top["종목명"], top["현재가"], top["등락률"], top["거래량"]])

    writer.writerow([])  # 빈 줄 구분

    # 뉴스 헤더 + 데이터
    writer.writerow(["[관련 뉴스]"])
    writer.writerow(["순번", "기사 제목", "링크"])
    for i, n in enumerate(news_list, 1):
        writer.writerow([i, n["제목"], n["링크"]])

    writer.writerow([])
    writer.writerow(["수집일시", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

print(f"\n  저장 완료: {filename}\n")
