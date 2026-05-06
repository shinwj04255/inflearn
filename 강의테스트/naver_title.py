import requests
import re

url = "https://www.naver.com"
response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
response.encoding = "utf-8"

match = re.search(r"<title>(.*?)</title>", response.text, re.IGNORECASE)
if match:
    print(f"title 태그 내용: {match.group(1)}")
else:
    print("title 태그를 찾지 못했습니다.")
