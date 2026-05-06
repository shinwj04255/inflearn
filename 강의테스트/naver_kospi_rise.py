import sys
import io
import requests
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

URL = "https://finance.naver.com/sise/sise_rise.nhn?sosok=0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

response = requests.get(URL, headers=headers)
response.encoding = "euc-kr"
soup = BeautifulSoup(response.text, "html.parser")

table = soup.select_one("table.type_2")
rows = table.select("tr")

stocks = []
for row in rows:
    cols = row.select("td")
    if len(cols) < 8:
        continue
    name_tag = cols[1].select_one("a")
    if not name_tag:
        continue
    name = name_tag.get_text(strip=True)
    price = cols[2].get_text(strip=True)
    change_rate = cols[4].get_text(strip=True)
    if name and price and change_rate:
        stocks.append((name, price, change_rate))
    if len(stocks) == 10:
        break

print(f"{'순위':<5} {'종목명':<15} {'현재가':>10} {'등락률':>8}")
print("-" * 42)
for i, (name, price, rate) in enumerate(stocks, 1):
    print(f"{i:<5} {name:<15} {price:>10} {rate:>8}")
