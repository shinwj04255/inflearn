import sys
import io
import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

# ── 1. 코스피 상승 종목 1등 가져오기 ─────────────────────────
rise_url = "https://finance.naver.com/sise/sise_rise.nhn?sosok=0"
res = requests.get(rise_url, headers=headers)
res.encoding = "euc-kr"
soup = BeautifulSoup(res.text, "html.parser")

table = soup.select_one("table.type_2")
filtered = []
for row in table.select("tr"):
    cols = row.select("td")
    if len(cols) < 5:
        continue
    name_tag = cols[1].select_one("a")
    if not name_tag:
        continue
    name = name_tag.get_text(strip=True)
    price_str = cols[2].get_text(strip=True)
    rate_str  = cols[4].get_text(strip=True)
    try:
        price = int(price_str.replace(",", ""))
        rate  = float(rate_str.replace("%", "").replace("+", "").replace(",", ""))
    except ValueError:
        continue
    if price >= 1_000 and rate >= 5.0:
        filtered.append((name, price, rate, rate_str))

filtered.sort(key=lambda s: s[2], reverse=True)
top_stock = filtered[0][0]
top_rate  = filtered[0][3]

print()
print(f"  1등 종목: {top_stock}  ({top_rate})")
print(f"  → 네이버 뉴스에서 '{top_stock}' 검색 중...")
print()

# ── 2. 네이버 뉴스 검색 (최신순) ─────────────────────────────
news_url = (
    "https://search.naver.com/search.naver"
    f"?where=news&query={requests.utils.quote(top_stock)}&sort=1"
)
res = requests.get(news_url, headers=headers)
soup = BeautifulSoup(res.text, "html.parser")

# href 중복 제거로 제목만 추출 (설명문 제외)
seen = set()
articles = []
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    # 뉴스 기사 링크 조건: 적당한 길이, 기사 URL, 미중복
    if (
        len(text) > 10
        and href not in seen
        and any(k in href for k in ["article", "news", "idxno", "view"])
        and "help.naver" not in href
        and "news.naver.com/main/static" not in href
    ):
        seen.add(href)
        articles.append((text, href))
    if len(articles) == 3:
        break

# ── 3. 출력 ──────────────────────────────────────────────────
print(f"  ['{top_stock}' 관련 최신 뉴스 TOP 3]")
print("  " + "─" * 66)
for i, (title, link) in enumerate(articles, 1):
    display = title if len(title) <= 60 else title[:59] + "…"
    print(f"  {i}. {display}")
    print(f"     {link}")
    print()
