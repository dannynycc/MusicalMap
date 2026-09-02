"""韓國 Interpark (NOL / world.nol.com) musicals — open JSON API.

API: /api/ent-channel-out/v1/goods/list?genreType=MUSICAL (paginated, no auth).
Gives REAL run dates (playStartDate/playEndDate — actual opening, unlike
Ticketmaster's availability window), venue name and posters. No coordinates —
we use a known-venue table for the major Korean houses plus Nominatim fallback
(", Seoul, South Korea" first — most are Seoul — then ", South Korea");
records that still fail are dropped and reported, never guessed.

Output: data/interpark.json   Run: python scrapers/interpark.py
"""

import json
import re
import sys
import io
import urllib.request
import urllib.parse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://world.nol.com/api/ent-channel-out/v1/goods/list"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# Major Korean venues (stable). Substring match, lowercase.
VENUES = {
    "blue square": ("BLUE SQUARE", "Seoul", 37.5409, 127.0028),
    "charlotte theater": ("Charlotte Theater", "Seoul", 37.5111, 127.0996),
    "lg arts center": ("LG Arts Center Seoul", "Seoul", 37.5664, 126.8270),
    "sejong": ("Sejong Center", "Seoul", 37.5725, 126.9760),
    "chungmu arts center": ("Chungmu Arts Center", "Seoul", 37.5663, 127.0181),
    "coex": ("Coex Artium", "Seoul", 37.5126, 127.0588),
    "uniplex": ("NOL Uniplex (大學路)", "Seoul", 37.5821, 127.0019),
    "yes24 art one": ("YES24 ART ONE (大學路)", "Seoul", 37.5817, 127.0034),
    "yes24 stage": ("YES24 Stage (大學路)", "Seoul", 37.5808, 127.0040),
    "national theater of korea": ("The National Theater of Korea", "Seoul", 37.5520, 127.0086),
    "seoul arts center": ("Seoul Arts Center", "Seoul", 37.4786, 127.0119),
    "doosan art center": ("Doosan Art Center", "Seoul", 37.5694, 127.0167),
    "hongik": ("Hongik Daehangno Art Center", "Seoul", 37.5797, 127.0035),
    "kwanglim": ("Kwanglim Arts Center", "Seoul", 37.5172, 127.0399),
    "myungbo art hall": ("Myungbo Art Hall", "Seoul", 37.5654, 126.9936),
    "dream art center": ("Dream Art Center (大學路)", "Seoul", 37.5810, 127.0048),
    "daehangno": ("大學路", "Seoul", 37.5817, 127.0027),
    "dae hak no": ("大學路 Art Madang", "Seoul", 37.5811, 127.0049),
    "mckithan": ("The McKithan Hotel (舊大韓劇場, 忠武路)", "Seoul", 37.5613, 126.9947),
    "galleria foret": ("Seoul Forest Galleria Foret", "Seoul", 37.5447, 127.0436),
    "jtn art hall": ("JTN Art Hall (大學路)", "Seoul", 37.5824, 127.0043),
    "myeongnyun art hall": ("Myeongnyun Art Hall", "Seoul", 37.5837, 126.9985),
    "myeongdong art center": ("Myeongdong NANTA Theater", "Seoul", 37.5636, 126.9869),
    "hongdae nanta": ("Hongdae NANTA Theater", "Seoul", 37.5571, 126.9244),
    "kyounghyang art hill": ("Kyounghyang Art Hill (貞洞)", "Seoul", 37.5560, 126.9716),
    # Non-Seoul venue: unknown venues default to Seoul (line ~130), so a Daegu hall
    # like DREAM HALL gets mis-placed unless listed here. (478 Apsansunhwan-ro, Nam-gu,
    # Daegu / 대덕문화전당, block-level geocode.)
    "dream hall": ("DREAM HALL (大邱 대덕문화전당)", "Daegu", 35.8331, 128.5835),
    # Daegu (DIMF circuit)
    "suseong artpia": ("Suseong Artpia", "Daegu", 35.8419, 128.6190),
    "ayang art center": ("Daegu Ayang Art Center", "Daegu", 35.8854, 128.6357),
    "bongsan cultural center": ("Daegu Bongsan Cultural Center", "Daegu", 35.8579, 128.5945),
    "daegu culture & arts centre": ("Daegu Culture & Arts Centre", "Daegu", 35.8533, 128.5586),
    "cgv daegu hanil": ("CGV Daegu Hanil", "Daegu", 35.8696, 128.5942),
}
KOREAN_CITIES = ["Seoul", "Busan", "Daegu", "Daejeon", "Incheon", "Gwangju", "Ulsan", "Suwon", "Goyang"]

# 韓文城市名 → 英文。city_hint 原本只比對英文,所以「오싹한 알바 - 부산」這種
# 韓文標題推不出城市,會掉進預設的 Seoul —— 那是【錯的城市】,不是缺值。
KO_CITY = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "대전": "Daejeon",
    "인천": "Incheon", "광주": "Gwangju", "울산": "Ulsan", "세종": "Sejong",
    "수원": "Suwon", "고양": "Goyang", "용인": "Yongin", "화성": "Hwaseong",
    "성남": "Seongnam", "안양": "Anyang", "부천": "Bucheon", "안산": "Ansan",
    "청주": "Cheongju", "천안": "Cheonan", "전주": "Jeonju", "창원": "Changwon",
    "안동": "Andong", "포항": "Pohang", "김해": "Gimhae", "춘천": "Chuncheon",
    "강릉": "Gangneung", "제주": "Jeju", "여수": "Yeosu", "익산": "Iksan",
}

# API 的 regionName → (城市, 地理編碼用的區域字串)。
# ⚠️ 有一半是【道(省級)】不是市:경기/강원/충북/충남/전북/경북/경남。
#    那些不能當城市名貼上去,只能當 Nominatim 的區域提示,城市改由標題或場館推。
REGION = {
    "Seoul": ("Seoul", "Seoul"),
    "부산시": ("Busan", "Busan"), "대구시": ("Daegu", "Daegu"),
    "인천시": ("Incheon", "Incheon"), "대전시": ("Daejeon", "Daejeon"),
    "광주시": ("Gwangju", "Gwangju"), "울산시": ("Ulsan", "Ulsan"),
    "세종시": ("Sejong", "Sejong"),
    "경기": (None, "Gyeonggi-do"), "강원": (None, "Gangwon-do"),
    "충북": (None, "Chungcheongbuk-do"), "충남": (None, "Chungcheongnam-do"),
    "전북": (None, "Jeollabuk-do"), "전남": (None, "Jeollanam-do"),
    "경북": (None, "Gyeongsangbuk-do"), "경남": (None, "Gyeongsangnam-do"),
    "제주": ("Jeju", "Jeju"),
}

# 道 → 該道底下的市。用途:regionName 只給到道級時,標題裡的城市名【必須屬於這個道】
# 才採用。2026-09-02 實例:「［청주,세종］뮤지컬…」@ 소극장 쇠내골,regionName=충북。
# 標題同時有 청주 與 세종(那是【巡演城市清單】不是場館所在地),不加這個檢查
# 會讓同一個場館一半標清州、一半標世宗 —— 世宗是獨立的特別自治市,不在충북。
PROVINCE_CITIES = {
    "Gyeonggi-do": {"Suwon", "Goyang", "Yongin", "Seongnam", "Hwaseong", "Anyang",
                    "Bucheon", "Ansan", "Icheon", "Gunpo", "Anseong", "Pocheon", "Hanam"},
    "Gangwon-do": {"Chuncheon", "Gangneung", "Wonju", "Yeongwol", "Inje"},
    "Chungcheongbuk-do": {"Cheongju", "Chungju", "Jecheon"},
    "Chungcheongnam-do": {"Cheonan", "Gongju", "Asan", "Boryeong"},
    "Jeollabuk-do": {"Jeonju", "Iksan", "Gunsan"},
    "Jeollanam-do": {"Yeosu", "Suncheon", "Mokpo"},
    "Gyeongsangbuk-do": {"Pohang", "Andong", "Gyeongju", "Gumi"},
    "Gyeongsangnam-do": {"Changwon", "Jinju", "Gimhae", "Yangsan"},
}

# Interpark 自己的分類會漏。魔術師 최현우 的 7 場裡只有 1 場被標 Non Verbal Performance,
# 其餘 6 場標成 Creation Musicals —— 子分類擋不住,只能點名。
# (與 poland.py 的 DROP_ARTISTS 同一個做法:來源把個人秀混進音樂劇分類。)
DROP_ACTS = ["최현우", "choi hyun woo", "합창단", "기획연주회"]

# 不是「舞台製作」的形式。2026-09-02 拿掉 globalType=EN 後才一起冒出來:
#   · 이머시브 다이닝 = 沉浸式餐飲(not_musical.json 的說明本來就把它列為排除對象)
#   · 리딩쇼케이스 / Reading-Showcase = 劇本朗讀會,不是正式製作
#   · 뮤지컬 콘서트 / Musical Concert = 音樂會版,不是舞台製作
#   · 「Subtitle]…」= 同一檔的字幕場次,與本體重複(WIDERSTAND 兩筆都在)
# ⚠️ 刻意【不】排除 음악극(音樂劇場)與 창극(唱劇):那是韓國自己的音樂戲劇類型,
#    不是「非音樂劇」,砍掉等於單方面刪掉一整個類別。
#   · 뮤지컬펍 / musical pub = 音樂劇【酒吧】。商品名是「입장권 구매」(入場券購買),
#     場館名就等於商品名(MusicalPub SpotLight),casting 全空 —— 賣的是進場消費,
#     不是一齣有劇情有角色的製作,與上面的沉浸式餐飲同類。2026-09-02 使用者要求
#     逐檔驗「到底是不是音樂劇」時抓到。
NOT_A_PRODUCTION = re.compile(
    r"이머시브\s*다이닝|immersive\s*dining|리딩\s*쇼케이스|reading[-\s]*showcase|"
    r"뮤지컬\s*콘서트|musical\s*concert|뮤지컬\s*펍|musical\s*pub|"
    r"^\s*[\[［]\s*subtitle\s*[\]］]", re.I)
# ⚠️ subtitle 那條要吃【全形】括號［］:實際標題是「［Subtitle］ Musical WIDERSTAND」,
#    第一版只寫半形 [] 完全沒擋到 —— 測了才發現,肉眼看兩者幾乎一樣。


# Service/merch products that NOL lists under MUSICAL but are not shows
# 2026-09-02 補 subtitle glasses / pre-order:拿掉 globalType=EN 後多抓到
# 「Dear Evan Hansen Subtitle Glasses Pre-order」——字幕眼鏡預購,不是演出。
# 原規則只認 caption glasses 與韓文的 자막,漏掉英文的 subtitle 寫法。
JUNK = re.compile(r"caption\s*glasses|subtitle\s*glasses|pre-?order|rental|자막|렌탈|주차|"
                  r"parking|package|패키지|goods|md\b|gift\s*card", re.I)


def clean_title(name):
    t = (name or "").strip()
    t = re.sub(r"^\s*(show\s+musical|musical\s*pub|musical|뮤지컬)\s*", "", t, flags=re.I)
    t = t.strip()
    t = re.sub(r"^[〈\[<(]\s*", "", t)
    t = re.sub(r"\s*[〉\]>)]\s*$", "", t)
    t = t.replace("〈", " ").replace("〉", " ").strip()
    return t or name.strip()


def city_hint(name):
    for c in KOREAN_CITIES[1:]:
        if re.search(rf"(?:^|[-–(\s]){c}\b", name, re.I):
            return c
    # 韓文城市名(標題常以「- 부산」「- 대구」標示巡演城市)
    for ko, en in KO_CITY.items():
        if ko in name:
            return en
    return None


def city_candidates(*texts):
    """把文字裡出現的【所有】城市名都收集起來(韓文與英文都比)。

    為什麼不能只取第一個:「［청주,세종］뮤지컬…」同時出現清州與世宗,那是
    【巡演城市清單】不是場館所在地;只取第一個會拿到世宗(場館其實在清州)。
    呼叫端再用 PROVINCE_CITIES 挑出屬於該道的那一個。
    英文也要比,因為城市名常常只出現在場館的英文名裡(Seongnam Arts Center)。
    """
    found, all_cities = [], set(KO_CITY.values()) | {c for s in PROVINCE_CITIES.values() for c in s}
    for name in texts:
        if not name:
            continue
        for ko, en in KO_CITY.items():
            if ko in name and en not in found:
                found.append(en)
        for en in all_cities:
            if re.search(rf"(?:^|[-–(\s]){en}\b", name, re.I) and en not in found:
                found.append(en)
    return found


def ticket_url(it):
    """購票連結:國際站 vs 韓國站要分開,選錯就是 404。

    🚨 2026-09-02 的 regression:那天拿掉 globalType=EN 之後多抓到的 75 檔是
    【只在韓國內銷】的場次,而 world.nol.com 是國際站 —— 它只放 globalType 非空的節目。
    結果那批的購票連結全部 404,佔當時韓國目錄的一半(46/92 組)。
    CI 不會發現,因為連結能不能開從來沒被檢查過。

    實測(4/4 乾淨對照):
      有 globalType(The Painters / LET ME FLY / Dracula 대구 / MIDNIGHT)→ world.nol.com 200
      無 globalType(물속의 달 / 목마와 숙녀 / 1457 / 놐놐놐)          → world.nol.com 404
    內銷場次的正確網址是 tickets.interpark.com/goods/{goodsCode}(已用瀏覽器實開確認,
    頁面帶完整劇情、卡司與類型標籤)。
    """
    gc, pc = it.get("goodsCode"), it.get("placeCode")
    if (it.get("globalType") or "").strip():
        return f"https://world.nol.com/en/ticket/places/{pc}/products/{gc}"
    return f"https://tickets.interpark.com/goods/{gc}"


def fetch_page(page):
    # ⚠️ 不要加回 globalType/languageType=EN。2026-09-02 實測:那兩個參數不是「翻譯成英文」,
    # 而是【只回國際夥伴節目】的篩選器 —— 帶著它只拿得到 58 檔,拿掉是 133 檔,
    # 而且 EN 的結果是 KR 的【嚴格子集】、同一檔在兩邊的 goodsName 完全相同
    # (不會讓既有英文劇名變成韓文)。多出來的 75 檔是首爾以外的地方製作居多
    # (大邱的 Dracula、仁川的 생텍쥐페리…),那正是我們原本整批看不到的盲區。
    qs = urllib.parse.urlencode({
        "goodsStatus": "Y,D",
        "genreType": "MUSICAL", "page": page, "size": 15, "includeNonPartnerGoods": "true",
    })
    req = urllib.request.Request(f"{API}?{qs}", headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))["data"]


def main():
    # NOTE: the API silently caps page size (requesting 50 still returns ~15),
    # and totalPages is computed from the REQUESTED size — don't trust it.
    # Page until empty / until we've collected totalElements.
    page, items, total = 1, [], None
    while page < 40:
        d = fetch_page(page)
        batch = d["content"]
        total = d.get("totalElements") or total
        if not batch:
            break
        items += batch
        if total and len(items) >= total:
            break
        page += 1
    print(f"{len(items)} musicals from NOL/Interpark API")

    shows, missing = [], []
    for it in items:
        raw_title = it.get("goodsName") or ""
        # Interpark 把【넌버벌 퍼포먼스】掛在 MUSICAL 這個大分類底下(Ca=Mus&SubCa=Non),
        # 但那些不是音樂劇:NANTA(난타)、JUMP、PAINTERS(現場作畫)、魔術師秀、跆拳道秀。
        # 2026-09-02 逐一看過該子類的 14 檔,沒有一檔是音樂劇 → 整個子類排除。
        # 用 subGenreName 從源頭擋,比事後用劇名比對可靠(페인터즈 有「- 고양」
        # 「- 서대문 전용관」「The Painters」「PAINTERS」等多種寫法)。
        if (it.get("subGenreName") or "").strip() == "Non Verbal Performance":
            continue
        if JUNK.search(raw_title):
            continue  # caption-glasses rental / parking / merch — not a show
        if any(a in raw_title.lower() for a in DROP_ACTS):
            continue  # 魔術師個人秀 / 合唱團公演 —— 來源誤掛在音樂劇分類下
        if NOT_A_PRODUCTION.search(raw_title):
            continue  # 沉浸式餐飲 / 劇本朗讀會 / 音樂會版 / 字幕重複場
        title = clean_title(raw_title)
        place = (it.get("placeName") or "").strip()
        if not title or not place:
            continue
        # 城市優先序:標題 → 場館名 → API 的 regionName。
        # ⚠️ 絕不再無條件 fallback 到 "Seoul":2026-09-02 拿掉 globalType=EN 之後
        #    才發現地方場次會被一律標成首爾(「오싹한 알바 - 부산」被標 Seoul),
        #    那是【錯的城市】不是缺值,會在地圖上把釜山的戲釘在首爾。
        rcity, rregion = REGION.get((it.get("regionName") or "").strip(), (None, None))
        # 🚨 regionName 是 API 的權威欄位,【優先於】從標題/場館名猜出來的城市。
        #    2026-09-02 實例:「세종문화회관 M씨어터」的 regionName=Seoul(正確,
        #    세종문화회관在首爾),但場館名含「세종」→ 猜成 Sejong → 連帶讓
        #    地理編碼查詢變成「…, Sejong, South Korea」→ Google 回世宗市的座標。
        #    【猜錯的城市會污染地理編碼,把場館搬到另一個城市去】,不只是標籤錯。
        if rcity:
            city = rcity                      # 廣域市:直接採用,不讓猜測覆蓋
        elif rregion:
            # 只到道級:從標題與場館名的【所有】候選城市裡,挑屬於這個道的那一個。
            ok = PROVINCE_CITIES.get(rregion, set())
            city = next((c for c in city_candidates(raw_title, place) if c in ok), None)
        else:
            city = city_hint(raw_title) or city_hint(place)
        vk = next((v for k, v in VENUES.items() if k in place.lower()), None)
        # 🚨 白名單是【子字串】比對,會把不同城市的同名場館併成一個。
        #    2026-09-02 實例:API 的「Sejong Culture and Arts Center (Jochiwon)」
        #    在【世宗市】,卻因為含 "sejong" 被對到首爾的세종문화회관,
        #    套上首爾座標 → 城市寫世宗、圖釘落在首爾的內部矛盾。
        #    所以:若已獨立判斷出城市、而且與白名單的城市不符,就視為誤配、不採用。
        if vk and city and vk[1] != city:
            vk = None
        if vk:
            venue, vcity, lat, lng = vk
            city = city or vcity
        else:
            venue = place
            # 地理編碼帶上區域,道級(경기/전북…)也能幫 Nominatim 收斂
            area = city or rregion
            city = city or rregion or "Seoul"
            lat, lng = geocode(f"{place}|{area}|kr".lower(), f"{place}, {area}, South Korea") \
                if area else (None, None)
            if lat is None:
                lat, lng = geocode(f"{place}|kr".lower(), f"{place}, South Korea")
        if lat is None:
            missing.append(f"{title} @ {place}")
            continue  # never guess a position

        gc = it.get("goodsCode")
        shows.append({
            "id": f"ip-{gc}",
            "title": title,
            "type": "tour",  # limited licensed seasons — card shows the real run range
            "venue": venue,
            "city": city,
            "country": "South Korea",
            "lat": lat,
            "lng": lng,
            "start_date": it.get("playStartDate") or None,
            "end_date": it.get("playEndDate") or None,
            "ticket_url": ticket_url(it),
            # posterImageUrl (…_p.gif) is the live poster; goodsLargeImageUrl often 404s
            "image": it.get("posterImageUrl") or it.get("goodsLargeImageUrl") or it.get("goodsSmallImageUrl"),
            "tour_name": None,
            "verified": True,
            "source": "world.nol.com (Interpark)",
        })

    out = {"meta": {"source": "world.nol.com (Interpark)", "count": len(shows),
                    "dropped_no_coords": missing}, "shows": shows}
    (DATA / "interpark.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    print(f"Wrote {len(shows)} shows -> data/interpark.json")
    if missing:
        print(f"⚠ dropped (no coords): {len(missing)}")
        for m in missing[:10]:
            print("   ", m)


if __name__ == "__main__":
    main()
