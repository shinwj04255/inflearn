import sys
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from bs4 import BeautifulSoup
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── 한글 폰트 설정 ────────────────────────────────────────────
_priority = ["Malgun Gothic", "Hancom Gothic", "HYGothic-Medium", "나눔고딕", "굴림"]
_available = {f.name for f in fm.fontManager.ttflist}
korean_font = next((f for f in _priority if f in _available), "DejaVu Sans")
plt.rcParams["font.family"] = korean_font
plt.rcParams["axes.unicode_minus"] = False

# ── 데이터 수집 ────────────────────────────────────────────────
URL = "https://finance.naver.com/sise/sise_rise.nhn?sosok=0"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
res = requests.get(URL, headers=headers)
res.encoding = "euc-kr"
soup = BeautifulSoup(res.text, "html.parser")

rows = []
for row in soup.select_one("table.type_2").select("tr"):
    cols = row.select("td")
    if len(cols) < 8:
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
    rows.append({"종목명": name, "현재가": price, "등락률": rate, "거래량": volume})

df_all = pd.DataFrame(rows)

# ── 필터링 & 정렬 ──────────────────────────────────────────────
df = (
    df_all[(df_all["현재가"] >= 1_000) & (df_all["등락률"] >= 5.0)]
    .sort_values("등락률", ascending=False)
    .reset_index(drop=True)
)
df.index += 1
df.index.name = "순위"

print(f"\n  수집: {len(df_all)}개 → 필터 후: {len(df)}개\n")
print(df[["종목명", "현재가", "등락률", "거래량"]].head(10).to_string())
print()

# ── 시각화 (2×2 대시보드) ──────────────────────────────────────
top20 = df.head(20).copy()
today = datetime.now().strftime("%Y-%m-%d %H:%M")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle(f"코스피 상승 종목 분석  |  {today}", fontsize=15, fontweight="bold", y=0.98)

colors = plt.cm.RdYlGn([r / top20["등락률"].max() for r in top20["등락률"]])

# ── 차트 1: 등락률 가로 막대 (TOP 20) ────────────────────────
ax1 = axes[0, 0]
bars = ax1.barh(top20["종목명"][::-1], top20["등락률"][::-1], color=colors[::-1])
ax1.set_xlabel("등락률 (%)")
ax1.set_title("등락률 TOP 20", fontweight="bold")
ax1.axvline(x=5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
for bar, val in zip(bars, top20["등락률"][::-1]):
    ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
             f"+{val:.1f}%", va="center", fontsize=7.5)

# ── 차트 2: 등락률 구간 히스토그램 ───────────────────────────
ax2 = axes[0, 1]
ax2.hist(df["등락률"], bins=15, color="#4C72B0", edgecolor="white", linewidth=0.8)
ax2.set_xlabel("등락률 (%)")
ax2.set_ylabel("종목 수")
ax2.set_title("등락률 분포 (5%↑ 종목 전체)", fontweight="bold")
ax2.axvline(df["등락률"].mean(), color="red", linestyle="--", linewidth=1.2,
            label=f"평균 {df['등락률'].mean():.1f}%")
ax2.legend(fontsize=9)

# ── 차트 3: 현재가 vs 등락률 산점도 ──────────────────────────
ax3 = axes[1, 0]
sc = ax3.scatter(df["현재가"], df["등락률"], c=df["거래량"],
                 cmap="YlOrRd", alpha=0.7, edgecolors="gray", linewidth=0.4, s=60)
plt.colorbar(sc, ax=ax3, label="거래량")
ax3.set_xlabel("현재가 (원)")
ax3.set_ylabel("등락률 (%)")
ax3.set_title("현재가 vs 등락률 (색=거래량)", fontweight="bold")
ax3.set_xscale("log")
for _, row in df.head(5).iterrows():
    ax3.annotate(row["종목명"], (row["현재가"], row["등락률"]),
                 fontsize=7, textcoords="offset points", xytext=(5, 3))

# ── 차트 4: 거래량 TOP 10 막대 ────────────────────────────────
ax4 = axes[1, 1]
top_vol = df.nlargest(10, "거래량").sort_values("거래량")
bar_colors = plt.cm.Blues([v / top_vol["거래량"].max() * 0.8 + 0.2 for v in top_vol["거래량"]])
ax4.barh(top_vol["종목명"], top_vol["거래량"] / 1_000_000, color=bar_colors)
ax4.set_xlabel("거래량 (백만 주)")
ax4.set_title("거래량 TOP 10", fontweight="bold")
for i, (_, row) in enumerate(top_vol.iterrows()):
    ax4.text(row["거래량"] / 1_000_000 + 0.3, i,
             f'{row["거래량"]:,}', va="center", fontsize=7.5)

plt.tight_layout()
out_file = f"kospi_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
plt.savefig(out_file, dpi=150, bbox_inches="tight")
print(f"  저장 완료: {out_file}")
plt.show()
