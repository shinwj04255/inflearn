import requests
from bs4 import BeautifulSoup

MARKET_CODE = {
    "KOSPI": 0,
    "KOSDAQ": 1,
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_top_gainers_combined(top_n: int = 15) -> list[dict]:
    kospi = get_top_gainers("KOSPI")
    kosdaq = get_top_gainers("KOSDAQ")
    combined = kospi + kosdaq
    combined.sort(key=lambda x: float(x["등락률"]) if x["등락률"] else 0, reverse=True)
    return combined[:top_n]


def get_top_gainers(market: str = "KOSPI") -> list[dict]:
    sosok = MARKET_CODE.get(market.upper())
    if sosok is None:
        raise ValueError(f"market은 'KOSPI' 또는 'KOSDAQ'이어야 합니다. 입력값: {market}")

    url = f"https://finance.naver.com/sise/sise_rise.naver?sosok={sosok}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.encoding = "euc-kr"

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one("table.type_2")
    if table is None:
        return []

    results = []
    for row in table.select("tr"):
        cols = row.select("td")
        # 유효한 데이터 행: 컬럼이 12개 이상이고 종목명 링크가 있어야 함
        if len(cols) < 12:
            continue
        name_tag = cols[1].select_one("a")
        if name_tag is None:
            continue

        name = name_tag.get_text(strip=True)
        href = name_tag.get("href", "")
        # href 예시: /item/main.naver?code=005930
        code = href.split("code=")[-1] if "code=" in href else ""

        def parse(text: str) -> str:
            return text.replace(",", "").replace("%", "").replace("+", "").strip()

        results.append(
            {
                "종목명": name,
                "종목코드": code,
                "시장": market.upper(),
                "현재가": parse(cols[2].get_text()),
                "등락률": parse(cols[4].get_text()),
                "거래량": parse(cols[6].get_text()),
                "거래대금": parse(cols[7].get_text()),
            }
        )

    return results


if __name__ == "__main__":
    print("[ 코스피 단독 상위 5개 ]")
    gainers = get_top_gainers("KOSPI")
    print(f"{'종목명':<12} {'종목코드':>8} {'현재가':>10} {'등락률(%)':>10} {'거래량':>12} {'거래대금(백만)':>16}")
    print("-" * 72)
    for stock in gainers[:5]:
        print(
            f"{stock['종목명']:<12} "
            f"{stock['종목코드']:>8} "
            f"{stock['현재가']:>10} "
            f"{stock['등락률']:>10} "
            f"{stock['거래량']:>12} "
            f"{stock['거래대금']:>16}"
        )

    print("\n[ 코스피 + 코스닥 합산 상위 15개 (등락률 순) ]")
    combined = get_top_gainers_combined(top_n=15)
    print(f"{'순위':>4} {'종목명':<12} {'종목코드':>8} {'시장':>6} {'현재가':>10} {'등락률(%)':>10} {'거래량':>12} {'거래대금(백만)':>16}")
    print("-" * 84)
    for rank, stock in enumerate(combined, start=1):
        print(
            f"{rank:>4} "
            f"{stock['종목명']:<12} "
            f"{stock['종목코드']:>8} "
            f"{stock['시장']:>6} "
            f"{stock['현재가']:>10} "
            f"{stock['등락률']:>10} "
            f"{stock['거래량']:>12} "
            f"{stock['거래대금']:>16}"
        )
