import sys
import io
import csv
from datetime import datetime
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

# 전체 데이터 수집
all_stocks = []
table = soup.select_one("table.type_2")
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
    all_stocks.append((name, price, price_str, rate, rate_str))

total = len(all_stocks)

# 필터링: 현재가 >= 1,000원 AND 등락률 >= 5%
filtered = [s for s in all_stocks if s[1] >= 1_000 and s[3] >= 5.0]

# 등락률 높은 순 정렬
filtered.sort(key=lambda s: s[3], reverse=True)

print()
print(f"  [전체 {total}개 종목 → 필터 조건 적용 후 {len(filtered)}개]")
print(f"  조건: 현재가 1,000원 이상  &  등락률 5% 이상  /  등락률 내림차순")
print()
print(f"  {'순위':>4}  {'종목명':<20}  {'현재가':>10}  {'등락률':>8}")
print("  " + "-" * 52)
for i, (name, price, price_str, rate, rate_str) in enumerate(filtered, 1):
    display = name if len(name) <= 18 else name[:17] + "…"
    print(f"  {i:>4}  {display:<20}  {price_str:>10}  {rate_str:>8}")

print()
print(f"  총 {len(filtered)}개 종목")
print()

# CSV 저장
filename = f"kospi_rise_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
with open(filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["순위", "종목명", "현재가", "등락률(%)"])
    for i, (name, price, price_str, rate, rate_str) in enumerate(filtered, 1):
        writer.writerow([i, name, price, rate])

print(f"  저장 완료: {filename}")
print()
