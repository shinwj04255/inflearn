import sys
import io
import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://finance.naver.com/sise/sise_rise.nhn?sosok=0"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

response = requests.get(URL, headers=headers)
response.encoding = "euc-kr"
soup = BeautifulSoup(response.text, "html.parser")

table = soup.select_one("table.type_2")
stocks = []
for row in table.select("tr"):
    cols = row.select("td")
    if len(cols) < 5:
        continue
    name_tag = cols[1].select_one("a")
    if not name_tag:
        continue
    name = name_tag.get_text(strip=True)
    price = cols[2].get_text(strip=True)
    rate_str = cols[4].get_text(strip=True)
    try:
        rate = float(rate_str.replace("%", "").replace("+", "").replace(",", ""))
    except ValueError:
        continue
    if name and rate_str:
        stocks.append((name, price, rate, rate_str))
    if len(stocks) == 10:
        break

MAX_BAR = 40
max_rate = max(s[2] for s in stocks)

print()
print("  코스피 상승 종목 TOP 10 — 등락률 막대 그래프")
print("  " + "=" * 70)
print()

for i, (name, price, rate, rate_str) in enumerate(stocks, 1):
    bar_len = int(rate / max_rate * MAX_BAR)
    bar = "█" * bar_len

    # 종목명을 20자 기준으로 맞춤 (한글은 2칸)
    display = f"{name[:14]:<14}" if len(name) <= 14 else name[:13] + "…"

    print(f"  {i:>2}. {display}  {bar:<40}  {rate_str:>7}  ({price}원)")

print()
print("  " + "=" * 70)
print(f"  기준: 최대 등락률 {max_rate:.2f}% = {'█' * MAX_BAR}")
print()
