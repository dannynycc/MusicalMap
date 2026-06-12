"""Curated Japan musical-theatre venues (user-supplied, all 47 prefectures).

Resident company houses (Shiki / Toho / Takarazuka) + every prefectural hall on
the national-tour circuit + 2.5D venues. Like tw_venues.py these populate the
My-Musicals autocomplete (bilingual JP/EN, building-level Google coords); they
aren't "currently playing" runs on the world map.

Run: python -u scrapers/jp_venues.py   (incremental; --all to redo)
Out: data/jp_venues.json  [{native, en, city, country, lat, lng}]
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

# (native name, city-English, geocode query). Resident Shiki/Toho/Takarazuka halls
# already arrive via the shiki/takarazuka scrapers, so this list focuses on the
# touring + commercial + 2.5D circuit the scrapers miss. A few flagships repeat for
# completeness; the catalog de-dupes by name+city.
VENUES = [
    # 専属/旗艦 flagship resident houses
    ("帝国劇場", "Tokyo", "帝国劇場 Imperial Theatre, Tokyo"),
    ("東急シアターオーブ", "Tokyo", "東急シアターオーブ Tokyu Theatre Orb, Shibuya"),
    ("東京建物 Brillia HALL", "Tokyo", "東京建物 Brillia HALL 豊島区"),
    ("シアタークリエ", "Tokyo", "シアタークリエ Theatre Creation, 千代田区"),
    ("日生劇場", "Tokyo", "日生劇場 Nissay Theatre, 千代田区"),
    ("新国立劇場 中劇場", "Tokyo", "新国立劇場 New National Theatre Tokyo, 渋谷区"),
    ("天王洲 銀河劇場", "Tokyo", "天王洲 銀河劇場 Galaxy Theatre, 品川区"),
    ("東京国際フォーラム ホールA", "Tokyo", "東京国際フォーラム Tokyo International Forum, 千代田区"),
    ("東京国際フォーラム ホールC", "Tokyo", "東京国際フォーラム Tokyo International Forum, 千代田区"),
    ("TOKYO DOME CITY HALL", "Tokyo", "東京ドームシティホール TOKYO DOME CITY HALL, 文京区"),
    ("品川プリンスホテル ステラボール", "Tokyo", "品川プリンスホテル ステラボール Stellar Ball"),
    ("日本青年館ホール", "Tokyo", "日本青年館ホール, 新宿区"),
    ("東京芸術劇場 プレイハウス", "Tokyo", "東京芸術劇場 Tokyo Metropolitan Theatre, 豊島区"),
    ("サンシャイン劇場", "Tokyo", "サンシャイン劇場 Sunshine Theatre, 池袋"),
    ("シアター1010", "Tokyo", "シアター1010 Theater 1010, 足立区"),
    ("IMM THEATER", "Tokyo", "IMM THEATER 文京区"),
    ("シアターGロッソ", "Tokyo", "シアターGロッソ 東京ドームシティ, 文京区"),
    # 神奈川 Kanagawa
    ("パシフィコ横浜 国立大ホール", "Yokohama", "パシフィコ横浜 国立大ホール PACIFICO Yokohama"),
    ("神奈川県民ホール", "Yokohama", "神奈川県民ホール Kanagawa Kenmin Hall, 横浜"),
    ("KT Zepp Yokohama", "Yokohama", "KT Zepp Yokohama, 横浜"),
    # 埼玉/千葉/茨城/群馬/栃木
    ("大宮ソニックシティ 大ホール", "Saitama", "大宮ソニックシティ Omiya Sonic City, さいたま市"),
    ("さいたまスーパーアリーナ", "Saitama", "さいたまスーパーアリーナ Saitama Super Arena"),
    ("千葉県文化会館", "Chiba", "千葉県文化会館 Chiba Prefectural Culture Hall"),
    ("市川市文化会館", "Ichikawa", "市川市文化会館 Ichikawa City Cultural Hall, 千葉県"),
    ("水戸市民会館", "Mito", "水戸市民会館 Mito Civic Hall, 茨城県"),
    ("高崎芸術劇場", "Takasaki", "高崎芸術劇場 Takasaki City Theatre, 群馬県"),
    ("宇都宮市文化会館", "Utsunomiya", "宇都宮市文化会館 Utsunomiya Culture Hall, 栃木県"),
    # 大阪 Osaka
    ("梅田芸術劇場 メインホール", "Osaka", "梅田芸術劇場 Umeda Arts Theater, 大阪市北区"),
    ("梅田芸術劇場 シアター・ドラマシティ", "Osaka", "梅田芸術劇場 シアター・ドラマシティ Drama City, 大阪"),
    ("SkyシアターMBS", "Osaka", "SkyシアターMBS Sky Theater MBS, 大阪市北区"),
    ("オリックス劇場", "Osaka", "オリックス劇場 Orix Theater, 大阪市西区"),
    ("フェスティバルホール", "Osaka", "フェスティバルホール Festival Hall, 大阪市北区"),
    ("COOL JAPAN PARK OSAKA WWホール", "Osaka", "COOL JAPAN PARK OSAKA WW Hall, 大阪城公園"),
    ("COOL JAPAN PARK OSAKA TTホール", "Osaka", "COOL JAPAN PARK OSAKA TT Hall, 大阪城公園"),
    ("新歌舞伎座", "Osaka", "新歌舞伎座 Shin-Kabukiza, 大阪市天王寺区"),
    # 兵庫/京都/近畿
    ("兵庫県立芸術文化センター KOBELCO大ホール", "Nishinomiya", "兵庫県立芸術文化センター Hyogo Performing Arts Center, 西宮市"),
    ("AiiA 2.5 Theater Kobe", "Kobe", "AiiA 2.5 Theater Kobe, 神戸市"),
    ("神戸国際会館 こくさいホール", "Kobe", "神戸国際会館 Kobe International House, 神戸市"),
    ("京都劇場", "Kyoto", "京都劇場 Kyoto Theatre, 京都駅"),
    ("びわ湖ホール", "Otsu", "びわ湖ホール Biwako Hall, 滋賀県大津市"),
    ("奈良県文化会館", "Nara", "奈良県文化会館 Nara Prefectural Culture Hall"),
    ("和歌山県民文化会館", "Wakayama", "和歌山県民文化会館 Wakayama Prefectural Culture Hall"),
    # 中部 Chubu
    ("御園座", "Nagoya", "御園座 Misonoza, 名古屋市"),
    ("愛知県芸術劇場 大ホール", "Nagoya", "愛知県芸術劇場 Aichi Arts Center, 名古屋市"),
    ("豊田市民文化会館", "Toyota", "豊田市民文化会館 Toyota City Cultural Hall, 愛知県"),
    ("静岡市民文化会館", "Shizuoka", "静岡市民文化会館 Shizuoka City Cultural Hall"),
    ("三重県文化会館", "Tsu", "三重県文化会館 Mie Prefectural Culture Hall, 津市"),
    ("りゅーとぴあ 新潟市民芸術文化会館", "Niigata", "りゅーとぴあ Ryutopia Niigata City Performing Arts Center"),
    ("富山県民会館", "Toyama", "富山県民会館 Toyama Prefectural Hall"),
    ("石川県立音楽堂", "Kanazawa", "石川県立音楽堂 Ishikawa Ongakudo, 金沢市"),
    ("福井市フェニックス・プラザ", "Fukui", "福井市フェニックス・プラザ Phoenix Plaza, 福井市"),
    ("ホクト文化ホール", "Nagano", "ホクト文化ホール 長野県県民文化会館, 長野市"),
    ("山梨県立県民文化ホール", "Kofu", "山梨県立県民文化ホール YCC, 甲府市"),
    # 九州/中国/四国
    ("博多座", "Fukuoka", "博多座 Hakataza, 福岡市"),
    ("キャナルシティ劇場", "Fukuoka", "キャナルシティ劇場 Canal City Theater, 福岡市"),
    ("福岡サンパレス ホール", "Fukuoka", "福岡サンパレス Fukuoka Sunpalace Hall"),
    ("北九州芸術劇場", "Kitakyushu", "北九州芸術劇場 Kitakyushu Performing Arts Center"),
    ("熊本城ホール", "Kumamoto", "熊本城ホール Kumamoto Castle Hall, 熊本市"),
    ("長崎ブリックホール", "Nagasaki", "長崎ブリックホール Nagasaki Brick Hall"),
    ("iichiko総合文化センター グランシアタ", "Oita", "iichiko総合文化センター iichiko Grand Theater, 大分市"),
    ("佐賀市文化会館", "Saga", "佐賀市文化会館 Saga City Cultural Hall"),
    ("川商ホール 鹿児島市民文化ホール", "Kagoshima", "川商ホール 鹿児島市民文化ホール, 鹿児島市"),
    ("宮崎市民文化ホール", "Miyazaki", "宮崎市民文化ホール Miyazaki Civic Cultural Hall"),
    ("広島文化学園HBGホール", "Hiroshima", "広島文化学園HBGホール HBG Hall, 広島市"),
    ("岡山芸術創造劇場 ハレnoわ", "Okayama", "岡山芸術創造劇場 ハレnoわ, 岡山市"),
    ("島根県民会館", "Matsue", "島根県民会館 Shimane Prefectural Hall, 松江市"),
    ("米子市公会堂", "Yonago", "米子市公会堂 Yonago Public Hall, 鳥取県"),
    ("愛媛県県民文化会館", "Matsuyama", "愛媛県県民文化会館 Ehime Prefectural Hall, 松山市"),
    ("高知県立県民文化ホール", "Kochi", "高知県立県民文化ホール Kochi Kenmin Hall"),
    ("香川県県民ホール レクザムホール", "Takamatsu", "香川県県民ホール Rexxam Hall, 高松市"),
    ("徳島市立文化センター", "Tokushima", "徳島市立文化センター Tokushima Cultural Center"),
    # 北海道/東北
    ("札幌文化芸術劇場 hitaru", "Sapporo", "札幌文化芸術劇場 hitaru, 札幌市"),
    ("仙台サンプラザホール", "Sendai", "仙台サンプラザホール Sendai Sunplaza Hall"),
    ("東京エレクトロンホール宮城", "Sendai", "東京エレクトロンホール宮城 宮城県民会館, 仙台市"),
    ("あきた芸術劇場 ミルハス", "Akita", "あきた芸術劇場 ミルハス Milhas, 秋田市"),
    ("岩手県民会館", "Morioka", "岩手県民会館 Iwate Prefectural Hall, 盛岡市"),
    ("リンクステーションホール青森", "Aomori", "リンクステーションホール青森 青森市民文化会館"),
    ("山形市民会館", "Yamagata", "山形市民会館 Yamagata Civic Hall"),
    ("郡山市民文化センター", "Koriyama", "郡山市民文化センター Koriyama Civic Cultural Center, 福島県"),
    # 沖縄
    ("那覇文化芸術劇場 なはーと", "Naha", "那覇文化芸術劇場 なはーと Nahaart, 那覇市"),
    ("沖縄コンベンションセンター 劇場棟", "Ginowan", "沖縄コンベンションセンター Okinawa Convention Center, 宜野湾市"),
]


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "jp_venues.json"
    existing = {v["native"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}

    out = []
    print(f"geocoding {len(VENUES)} Japan venues", flush=True)
    for i, (native, city, query) in enumerate(VENUES, 1):
        if not force and native in existing and existing[native].get("lat"):
            out.append(existing[native]); continue
        r = gg.places_new(query, key)
        time.sleep(0.08)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng = round(r[0], 6), round(r[1], 6)
            r2 = gg.places_new(query, key, language="en"); time.sleep(0.08)
            en = r2[2] if (isinstance(r2, tuple) and r2 and r2[0] != "DENIED" and len(r2) >= 3) else r[2]
            rec = {"native": native, "en": en, "city": city, "country": "Japan", "lat": lat, "lng": lng}
            print(f"  [{i}/{len(VENUES)}] {native} → {en} @ {lat},{lng}", flush=True)
        else:
            rec = {"native": native, "en": "", "city": city, "country": "Japan", "lat": None, "lng": None}
            print(f"  [{i}/{len(VENUES)}] {native} → NO RESULT (manual)", flush=True)
        out.append(rec)

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in out if v.get("lat"))
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/jp_venues.json", flush=True)


if __name__ == "__main__":
    main()
