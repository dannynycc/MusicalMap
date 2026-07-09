"""哨兵劇目體檢 — 「不可能不在地圖上」的常設劇清單,build 後對照 shows.json。

動機(2026-07-09 資料品質戰役):維也納 VBW 歸零、broadway 28→16 都是「來源壞掉但
無人知道」;來源筆數守門(build_shows)抓「驟降」,這裡抓「該在而不在」——兩者互補:
守門對付突然壞,哨兵對付長期漏(如 Bochum 星光快車從未被任何來源覆蓋)。

清單原則:只收「開放式常設、非輪換檔期」的鐵桿駐演——會下檔的劇不進來(誤報比漏報傷)。
劇目真閉幕時(如 2026-06 Death Becomes Her)從清單移除即可。

輸出:每缺一項印一行 GitHub Actions ::warning(不擋 build)。
Run: python scrapers/audit_sentinels.py
"""

import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"

# (title 關鍵字, city 關鍵字, 備註)。比對不分大小寫,title 對 title+tour_name。
SENTINELS = [
    ("Lion King", "New York", "百老匯獅子王(1997-)"),
    ("Wicked", "New York", "百老匯 Wicked(2003-)"),
    ("Lion King", "London", "西區獅子王(1999-)"),
    ("Les Mis", "London", "西區悲慘世界(1985-)"),
    ("Phantom", "London", "西區歌劇魅影(1986-)"),
    ("Mamma Mia", "London", "西區媽媽咪呀"),
    ("Lion King", "Hamburg", "漢堡獅子王(2001-,Stage 常設)"),
    ("Starlight Express", "Bochum", "波鴻星光快車(1988-,專用劇場)"),
    ("Lion King", "Madrid", "馬德里獅子王(Lope de Vega 常設)"),
    ("Lion King", "Tokyo", "東京獅子王(四季,1998-)"),
    ("Aladdin", "Tokyo", "東京阿拉丁(四季,2015-)"),
    ("Book of Mormon", "New York", "百老匯摩門經(2011-)"),
]

# 來源最低筆數哨兵(該來源正常時遠高於此;掉破線=來源壞了)
SOURCE_FLOORS = {
    "opentix.life": 20,
    "londontheatre.co.uk": 25,
    "broadway-show-tickets.com": 18,
    "musicalvienna.at": 1,
    "shiki.jp": 8,
    "interpark": 10,
    "damai": 80,
}


def main():
    d = json.loads((DATA / "shows.json").read_text(encoding="utf-8"))
    shows = d["shows"]
    miss = 0
    for kw, city, note in SENTINELS:
        ok = any(
            kw.lower() in (s["title"] + " " + str(s.get("tour_name"))).lower()
            and city.lower() in str(s.get("city", "")).lower()
            for s in shows
        )
        if not ok:
            miss += 1
            print(f"::warning::sentinel missing: {note}({kw} @ {city})不在 shows.json — 對應來源可能壞了")
    src_count = {}
    for s in shows:
        k = (s.get("source") or "?").lower()   # 不分大小寫:interpark 改名後 source="world.nol.com (Interpark)"(首跑誤報教訓)
        src_count[k] = src_count.get(k, 0) + 1
    for src, floor in SOURCE_FLOORS.items():
        n = sum(v for k, v in src_count.items() if src.lower() in k)
        if n < floor:
            miss += 1
            print(f"::warning::sentinel source floor: {src} 只有 {n} 筆(低標 {floor})")
    print(f"sentinel audit: {len(SENTINELS)} 劇目+{len(SOURCE_FLOORS)} 來源低標,{'全過 ✓' if miss == 0 else f'{miss} 項告警'}")
    # 不擋 build:return 0;CI 靠 ::warning 顯示
    return 0


if __name__ == "__main__":
    sys.exit(main())
