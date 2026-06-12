"""Curated South Korea musical-theatre venues (user-supplied).

Seoul's big resident musical houses + Daehangno small-theatre clusters + the
regional Arts-Center touring circuit. Trilingual: Korean (native, via Google),
English, and the Chinese names the user supplied — all go into the search blob so
either script finds the venue. Populates the My-Musicals autocomplete.

Run: python -u scrapers/kr_venues.py   (incremental; --all to redo)
Out: data/kr_venues.json  [{native, en, zh, city, country, lat, lng}]
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

# (Chinese name, English name, city-English, geocode query)
VENUES = [
    # 首爾 Seoul — major musical houses
    ("夏洛特劇院", "Charlotte Theater", "Seoul", "Charlotte Theater, Songpa, Seoul"),
    ("藍色廣場 新韓卡演藝廳", "Blue Square Shinhan Card Hall", "Seoul", "Blue Square, Hannam, Yongsan, Seoul"),
    ("世宗文化會館 大劇場", "Sejong Center Grand Theater", "Seoul", "Sejong Center for the Performing Arts, Seoul"),
    ("藝術殿堂 歌劇院", "Seoul Arts Center Opera House", "Seoul", "Seoul Arts Center Opera House, Seocho"),
    ("藝術殿堂 CJ土月劇場", "Seoul Arts Center CJ Towol Theater", "Seoul", "Seoul Arts Center CJ Towol Theater, Seocho"),
    ("LG藝術中心 首爾", "LG Arts Center Seoul", "Seoul", "LG Arts Center Seoul, Magok, Gangseo"),
    ("D-Cube藝術中心", "D-Cube Link Arts Center", "Seoul", "Link Art Center D-Cube, Guro, Seoul"),
    ("光林藝術中心 BBCH廳", "Kwanglim Arts Center BBCH Hall", "Seoul", "Kwanglim Arts Center, Sinsa, Gangnam, Seoul"),
    ("忠武藝術中心 大劇場", "Chungmu Arts Center Grand Theater", "Seoul", "Chungmu Arts Center, Jung-gu, Seoul"),
    ("國立劇場 海升劇場", "National Theater of Korea Haeoreum", "Seoul", "National Theater of Korea, Jung-gu, Seoul"),
    # 首爾 大學路 Daehangno cluster (Jongno)
    ("連結藝術中心 大學路", "Link Arts Center Daehangno", "Seoul", "Link Art Center Daehangno, Jongno, Seoul"),
    ("Plus Theater 大學路", "Plus Theater", "Seoul", "Plus Theater Daehangno, Jongno, Seoul"),
    ("YES24 STAGE 大學路", "YES24 Stage", "Seoul", "YES24 Stage, Daehangno, Jongno, Seoul"),
    ("TOM劇場 大學路", "TOM Theater", "Seoul", "TOM Theater, Daehangno, Jongno, Seoul"),
    ("DREAM THEATER 大學路", "Dream Theater Daehangno", "Seoul", "Dream Theater Daehangno, Jongno, Seoul"),
    ("JTN劇場 大學路", "JTN Theater", "Seoul", "JTN Art Hall, Daehangno, Jongno, Seoul"),
    ("弘大大學路藝術中心", "Hongik Univ Daehangno Art Center", "Seoul", "Hongik University Daehangno Art Center, Jongno, Seoul"),
    ("誠信女子大學 雲庭綠色校園大禮堂", "Sungshin Women's Univ Auditorium", "Seoul", "Sungshin Women's University, Gangbuk, Seoul"),
    ("同德女子大學 表演藝術中心", "Dongduk Women's Univ Performing Arts Center", "Seoul", "Dongduk Women's University Performing Arts Center, Jongno, Seoul"),
    # 釜山 Busan
    ("釜山夢想劇場", "Dream Theatre Busan", "Busan", "Dream Theatre, Munhyeon, Nam-gu, Busan"),
    ("釜山市民會館 大劇場", "Busan Citizens Hall Grand Theater", "Busan", "Busan Citizens Hall, Dong-gu, Busan"),
    ("釜山文化會館 大劇場", "Busan Cultural Center Grand Theater", "Busan", "Busan Cultural Center, Nam-gu, Busan"),
    ("電影殿堂 Sohyang劇場", "Sohyang Theater Shinhan Card Hall", "Busan", "Sohyang Theatre, Centum City, Haeundae, Busan"),
    # 大邱 Daegu
    ("大邱歌劇院", "Daegu Opera House", "Daegu", "Daegu Opera House, Buk-gu, Daegu"),
    ("啟明藝術中心", "Keimyung Art Center", "Daegu", "Keimyung Art Center, Dalseo, Daegu"),
    ("大邱文化藝術會館 八公廳", "Daegu Culture & Arts Center", "Daegu", "Daegu Culture and Arts Center, Daegu"),
    ("壽城藝術中心", "Suseong Artpia", "Daegu", "Suseong Artpia, Suseong, Daegu"),
    ("鳳山文化會館", "Bongsan Cultural Center", "Daegu", "Bongsan Cultural Center, Jung-gu, Daegu"),
    # 京畿道 Gyeonggi
    ("高陽 Aram Nuri 歌劇院", "Goyang Aram Nuri Arts Center", "Goyang", "Goyang Aram Nuri Arts Center, Goyang"),
    ("城南藝術中心 大劇場", "Seongnam Arts Center", "Seongnam", "Seongnam Arts Center, Bundang, Seongnam"),
    ("龍仁包恩藝術中心", "Yongin Poeun Art Hall", "Yongin", "Yongin Poeun Art Hall, Yongin"),
    ("水原 SK 藝術中心", "Suwon SK Artrium", "Suwon", "Suwon SK Artrium, Suwon"),
    ("京畿藝術殿堂", "Gyeonggi Arts Center", "Suwon", "Gyeonggi Arts Center, Suwon"),
    ("安山文化藝術殿堂", "Ansan Arts Center", "Ansan", "Ansan Arts Center, Ansan"),
    ("議政府藝術殿堂", "Uijeongbu Arts Center", "Uijeongbu", "Uijeongbu Arts Center, Uijeongbu"),
    ("富川市民文化會館", "Bucheon City Hall", "Bucheon", "Bucheon City Hall Concert, Bucheon"),
    ("軍浦文化藝術會館", "Gunpo Cultural Arts Center", "Gunpo", "Gunpo Cultural Arts Center, Gunpo"),
    # 仁川 Incheon
    ("仁川文化藝術會館 大劇場", "Incheon Culture & Arts Center", "Incheon", "Incheon Culture and Arts Center, Namdong, Incheon"),
    ("仁川藝術中心", "Art Center Incheon", "Incheon", "Art Center Incheon, Songdo, Incheon"),
    ("富平藝術中心", "Bupyeong Art Center", "Incheon", "Bupyeong Art Center, Incheon"),
    # 中部/湖南/嶺南 regional
    ("大田藝術殿堂 大劇場", "Daejeon Arts Center", "Daejeon", "Daejeon Arts Center, Daejeon"),
    ("光州文化藝術會館", "Gwangju Arts Center", "Gwangju", "Gwangju Culture and Art Center, Gwangju"),
    ("國立亞洲文化殿堂 藝術劇場", "Asia Culture Center (ACC) Theater", "Gwangju", "National Asian Culture Center ACC, Gwangju"),
    ("蔚山文化藝術會館", "Ulsan Culture & Arts Center", "Ulsan", "Ulsan Culture and Arts Center, Ulsan"),
    ("慶南文化藝術會館", "Gyeongnam Culture & Arts Center", "Jinju", "Gyeongnam Culture and Arts Center, Jinju"),
    ("昌原城山藝術廳", "Changwon Seongsan Art Hall", "Changwon", "Seongsan Art Hall, Changwon"),
    ("全北特別自治道藝術殿堂", "Jeonbuk Arts Center", "Jeonju", "Hanguk Sori Arts Center / Jeonbuk Arts Center, Jeonju"),
    ("清州藝術殿堂", "Cheongju Arts Center", "Cheongju", "Cheongju Arts Center, Cheongju"),
    ("天安藝術殿堂", "Cheonan Arts Center", "Cheonan", "Cheonan Arts Center, Cheonan"),
    # 濟州 Jeju
    ("濟州文化藝術會館", "Jeju Culture & Arts Center", "Jeju", "Jeju Culture and Arts Center, Jeju"),
    ("濟州藝術中心", "Jeju Arts Center", "Jeju", "Jeju Arts Center, Jeju"),
]


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "kr_venues.json"
    existing = {v["zh"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}

    out = []
    print(f"geocoding {len(VENUES)} Korea venues", flush=True)
    for i, (zh, en, city, query) in enumerate(VENUES, 1):
        if not force and zh in existing and existing[zh].get("lat"):
            out.append(existing[zh]); continue
        r = gg.places_new(query, key)
        time.sleep(0.08)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng = round(r[0], 6), round(r[1], 6)
            r2 = gg.places_new(query, key, language="ko"); time.sleep(0.08)
            native = r2[2] if (isinstance(r2, tuple) and r2 and r2[0] != "DENIED" and len(r2) >= 3) else r[2]
            rec = {"native": native, "en": en, "zh": zh, "city": city, "country": "South Korea", "lat": lat, "lng": lng}
            print(f"  [{i}/{len(VENUES)}] {zh} / {en} → native='{native}' @ {lat},{lng}", flush=True)
        else:
            rec = {"native": "", "en": en, "zh": zh, "city": city, "country": "South Korea", "lat": None, "lng": None}
            print(f"  [{i}/{len(VENUES)}] {zh} → NO RESULT (manual)", flush=True)
        out.append(rec)

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in out if v.get("lat"))
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/kr_venues.json", flush=True)


if __name__ == "__main__":
    main()
