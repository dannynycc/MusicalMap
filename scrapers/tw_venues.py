"""Curated Taiwan musical-theatre venues (user-supplied, exhaustive by region).

These are halls with a public ticketed history of musicals across Taiwan. They
have no single "currently playing" run, so they aren't shows on the world map —
they populate the My-Musicals autocomplete so a Taiwanese user can log the exact
local hall they attended. We Google-geocode each for a building-level coordinate
and an English name, and keep the Chinese name for bilingual display/search.

Run: python -u scrapers/tw_venues.py   (incremental; --all to redo)
Out: data/tw_venues.json  [{zh, en, city, country, lat, lng}]
KEY: env GOOGLE_MAPS_KEY or scrapers/.gmaps_key (gitignored).
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

import importlib.util
_spec = importlib.util.spec_from_file_location("gg", ROOT / "scrapers" / "geocode_google.py")
gg = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(gg)

# (Chinese display name, city-English, geocode query). The query targets the
# parent building so halls in the same complex resolve to the right coordinate.
VENUES = [
    # 臺北市 Taipei
    ("國家戲劇院", "Taipei", "國家戲劇院 National Theater, Taipei"),
    ("國家兩廳院 實驗劇場", "Taipei", "國家戲劇院 National Theater, Taipei"),
    ("台北小巨蛋", "Taipei", "台北小巨蛋 Taipei Arena"),
    ("台北流行音樂中心 表演廳", "Taipei", "臺北流行音樂中心 Taipei Music Center"),
    ("臺北表演藝術中心 大劇院", "Taipei", "臺北表演藝術中心 Taipei Performing Arts Center"),
    ("臺北表演藝術中心 球劇場", "Taipei", "臺北表演藝術中心 Taipei Performing Arts Center"),
    ("臺北表演藝術中心 藍盒子", "Taipei", "臺北表演藝術中心 Taipei Performing Arts Center"),
    ("臺北市政府親子劇場", "Taipei", "臺北市政府親子劇場, Taipei"),
    ("國立臺灣藝術教育館 南海劇場", "Taipei", "國立臺灣藝術教育館 南海劇場, Taipei"),
    ("水源劇場", "Taipei", "水源劇場 Shuiyuan Theatre, Taipei"),
    ("PLAYground 南村劇場", "Taipei", "PLAYground 南村劇場, Taipei"),
    ("萬座曉劇場", "Taipei", "萬座曉劇場, Taipei"),
    ("臺北市客家音樂戲劇中心", "Taipei", "臺北市客家音樂戲劇中心, Taipei"),
    ("CORNER MAX 大角落多功能展演館", "Taipei", "CORNER MAX 大角落, Taipei"),
    ("華山1914 烏梅劇院", "Taipei", "華山1914 烏梅劇院, Taipei"),
    ("大稻埕戲苑", "Taipei", "大稻埕戲苑 Dadaocheng Theater, Taipei"),
    ("國立臺灣大學 鹿鳴堂／藝文中心", "Taipei", "國立臺灣大學 鹿鳴堂, Taipei"),
    # 新北市 New Taipei
    ("新北市藝文中心 演藝廳", "New Taipei", "新北市藝文中心, New Taipei"),
    ("臺灣戲曲中心 大表演廳", "Taipei", "臺灣戲曲中心 Taiwan Traditional Theatre Center"),
    ("臺灣戲曲中心 小表演廳", "Taipei", "臺灣戲曲中心 Taiwan Traditional Theatre Center"),
    ("國立臺灣藝術大學 臺藝表演廳", "New Taipei", "國立臺灣藝術大學, New Taipei"),
    ("樹林藝文中心 演藝廳", "New Taipei", "樹林藝文中心, New Taipei"),
    # 基隆市 Keelung
    ("基隆文化中心 演藝廳（基隆表演藝術中心）", "Keelung", "基隆文化中心 演藝廳, Keelung"),
    # 桃園市 Taoyuan
    ("桃園展演中心 展演廳", "Taoyuan", "桃園展演中心, Taoyuan"),
    ("中壢藝術館 音樂廳", "Taoyuan", "中壢藝術館, Zhongli, Taoyuan"),
    ("廣藝廳", "Taoyuan", "廣藝廳 Quanta Hall, Linkou"),
    # 新竹 Hsinchu
    ("新竹市文化局演藝廳", "Hsinchu", "新竹市文化局演藝廳, Hsinchu"),
    ("新竹縣政府文化局 演藝廳", "Zhubei", "新竹縣政府文化局 演藝廳, Zhubei"),
    ("國立陽明交通大學 演藝廳", "Hsinchu", "國立陽明交通大學 演藝廳, Hsinchu"),
    # 苗栗縣 Miaoli
    ("苗栗縣政府文化觀光局 中正堂", "Miaoli", "苗栗縣政府文化觀光局, Miaoli"),
    ("苗北藝文中心 演藝廳", "Miaoli", "苗北藝文中心, Zhunan, Miaoli"),
    # 臺中市 Taichung
    ("臺中國家歌劇院 大劇院", "Taichung", "臺中國家歌劇院 National Taichung Theater"),
    ("臺中國家歌劇院 中劇院", "Taichung", "臺中國家歌劇院 National Taichung Theater"),
    ("臺中國家歌劇院 小劇場", "Taichung", "臺中國家歌劇院 National Taichung Theater"),
    ("台中市中山堂", "Taichung", "臺中市中山堂 Taichung Zhongshan Hall"),
    ("屯區藝文中心 演藝廳", "Taichung", "屯區藝文中心, Taichung"),
    ("葫蘆墩文化中心 演奏廳", "Taichung", "葫蘆墩文化中心, Fengyuan, Taichung"),
    # 彰化縣 Changhua
    ("員林演藝廳 表演廳", "Changhua", "員林演藝廳, Yuanlin, Changhua"),
    ("彰化縣政府文化局 演藝廳", "Changhua", "彰化縣政府文化局 演藝廳, Changhua"),
    # 南投縣 Nantou
    ("南投縣政府文化局 演藝廳", "Nantou", "南投縣政府文化局 演藝廳, Nantou"),
    # 雲林縣 Yunlin
    ("雲林縣表演廳", "Yunlin", "雲林縣表演廳, Douliu, Yunlin"),
    # 嘉義 Chiayi
    ("嘉義縣表演藝術中心 演藝廳", "Chiayi", "嘉義縣表演藝術中心, Minxiong, Chiayi"),
    ("嘉義市政府文化局 音樂廳", "Chiayi", "嘉義市政府文化局 音樂廳, Chiayi"),
    # 臺南市 Tainan
    ("臺南文化中心 演藝廳", "Tainan", "臺南文化中心 Tainan Cultural Center"),
    ("新營文化中心 演藝廳", "Tainan", "新營文化中心, Xinying, Tainan"),
    ("台南人戲工廠", "Tainan", "台南人戲工廠 台南市東區"),
    # 高雄市 Kaohsiung
    ("衛武營國家藝術文化中心 歌劇院", "Kaohsiung", "衛武營國家藝術文化中心 National Kaohsiung Center for the Arts Weiwuying"),
    ("衛武營國家藝術文化中心 戲劇院", "Kaohsiung", "衛武營國家藝術文化中心 Weiwuying, Kaohsiung"),
    ("衛武營國家藝術文化中心 表演廳", "Kaohsiung", "衛武營國家藝術文化中心 Weiwuying, Kaohsiung"),
    ("高雄市文化中心 至德堂", "Kaohsiung", "高雄市文化中心 至德堂, Kaohsiung"),
    ("高雄流行音樂中心 海音館", "Kaohsiung", "高雄流行音樂中心 Kaohsiung Music Center"),
    ("高雄市社教館 演藝廳", "Kaohsiung", "高雄市立社會教育館, Kaohsiung"),
    ("大東文化藝術中心 演藝廳", "Kaohsiung", "大東文化藝術中心, Fengshan, Kaohsiung"),
    # 屏東縣 Pingtung
    ("屏東藝術館", "Pingtung", "屏東藝術館, Pingtung"),
    ("屏東演藝廳", "Pingtung", "屏東演藝廳 Pingtung Performing Arts Center"),
    # 東部及離島 East & Islands
    ("花蓮縣文化局演藝堂", "Hualien", "花蓮縣文化局演藝堂, Hualien"),
    ("臺東縣政府文化處藝文中心 演藝廳", "Taitung", "臺東縣藝文中心 演藝廳, Taitung"),
    ("宜蘭演藝廳", "Yilan", "宜蘭演藝廳, Yilan"),
    ("澎湖縣演藝廳", "Penghu", "澎湖縣演藝廳, Magong, Penghu"),
    ("金門縣文化局 演藝廳", "Kinmen", "金門縣文化局 演藝廳, Kinmen"),
    ("馬祖南竿介壽堂", "Lienchiang", "馬祖南竿介壽堂, Nangan, Lienchiang"),
]


# Hardcoded English names where Google's is wrong/ambiguous (overrides geocode).
EN_OVERRIDE = {
    "國家戲劇院": "National Theater and Concert Hall",
    "國家兩廳院 實驗劇場": "National Theater and Concert Hall (Experimental Theater)",
}


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "tw_venues.json"
    existing = {v["zh"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}

    out = []
    print(f"geocoding {len(VENUES)} Taiwan venues", flush=True)
    for i, (zh, city, query) in enumerate(VENUES, 1):
        if not force and zh in existing and existing[zh].get("lat"):
            out.append(existing[zh]); continue
        r = gg.places_new(query, key)
        time.sleep(0.08)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng, gname = round(r[0], 6), round(r[1], 6), r[2]
            en = gname if all(ord(c) < 128 for c in gname) else None
            if not en:  # ask Google for the English name explicitly
                r2 = gg.places_new(query, key, language="en"); time.sleep(0.08)
                en = r2[2] if (isinstance(r2, tuple) and r2 and r2[0] != "DENIED" and len(r2) >= 3) else gname
            en = EN_OVERRIDE.get(zh, en)
            rec = {"zh": zh, "en": en, "city": city, "country": "Taiwan", "lat": lat, "lng": lng}
            print(f"  [{i}/{len(VENUES)}] {zh} → {en} @ {lat},{lng}", flush=True)
        else:
            rec = {"zh": zh, "en": "", "city": city, "country": "Taiwan", "lat": None, "lng": None}
            print(f"  [{i}/{len(VENUES)}] {zh} → NO RESULT (manual)", flush=True)
        out.append(rec)

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in out if v.get("lat"))
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/tw_venues.json", flush=True)


if __name__ == "__main__":
    main()
