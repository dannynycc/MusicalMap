"""Curated Mainland China large-scale musical-theatre venues (user-supplied).

The national-tour circuit (Poly / China Arts theatre chains + landmark grand
theatres, 1,200+ seats with orchestra pit & full fly tower). Bilingual EN/中文;
search_blob adds simplified+traditional so either script matches. Populates the
My-Musicals autocomplete (no "currently playing" run → not on the world map).

Run: python -u scrapers/cn_venues.py   (incremental; --all to redo)
Out: data/cn_venues.json  [{native, en, city, country, lat, lng}]
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
    # 上海 Shanghai
    ("上海文化廣場", "Shanghai Culture Square", "Shanghai", "上海文化广场 Shanghai Culture Square"),
    ("上海大劇院", "Shanghai Grand Theatre", "Shanghai", "上海大剧院 Shanghai Grand Theatre"),
    ("上海東方藝術中心 歌劇廳", "Shanghai Oriental Art Center", "Shanghai", "上海东方艺术中心 Shanghai Oriental Art Center"),
    ("上海美琪大戲院", "Majestic Theatre Shanghai", "Shanghai", "美琪大戏院 Majestic Theatre, Shanghai"),
    ("上海大寧劇院", "Shanghai Daning Theatre", "Shanghai", "上海大宁剧院 Daning Theatre, Shanghai"),
    ("前灘31演藝中心 大劇場", "Qiantan 31 Performing Arts Center", "Shanghai", "前滩31演艺中心 Qiantan 31, Shanghai"),
    # 北京 Beijing
    ("北京天橋藝術中心 大劇場", "Beijing Tianqiao Performing Arts Center", "Beijing", "北京天桥艺术中心 Tianqiao Performing Arts Center, Beijing"),
    ("國家大劇院 歌劇院", "National Centre for the Performing Arts (NCPA)", "Beijing", "国家大剧院 National Centre for the Performing Arts, Beijing"),
    ("北京保利劇院", "Beijing Poly Theatre", "Beijing", "北京保利剧院 Poly Theatre, Beijing"),
    ("北京世紀劇院", "Beijing Century Theatre", "Beijing", "北京世纪剧院 Century Theatre, Beijing"),
    ("北京天橋劇場", "Beijing Tianqiao Theatre", "Beijing", "北京天桥剧场 Tianqiao Theatre, Beijing"),
    ("北京二七劇場", "Beijing Erqi Theatre", "Beijing", "北京二七剧场, Beijing"),
    ("北京展覽館劇場", "Beijing Exhibition Theatre", "Beijing", "北京展览馆剧场 Beijing Exhibition Theatre"),
    # 重慶 Chongqing
    ("重慶大劇院", "Chongqing Grand Theatre", "Chongqing", "重庆大剧院 Chongqing Grand Theatre"),
    ("重慶施光南大劇院", "Chongqing Shi Guangnan Grand Theatre", "Chongqing", "重庆施光南大剧院, Chongqing"),
    # 天津 Tianjin
    ("天津大劇院 歌劇廳", "Tianjin Grand Theatre", "Tianjin", "天津大剧院 Tianjin Grand Theatre"),
    ("天津武清影劇院", "Tianjin Wuqing Theatre", "Tianjin", "天津武清影剧院, Tianjin"),
    # 江蘇 Jiangsu
    ("江蘇大劇院 歌劇廳", "Jiangsu Grand Theatre", "Nanjing", "江苏大剧院 Jiangsu Grand Theatre, Nanjing"),
    ("南京保利大劇院", "Nanjing Poly Grand Theatre", "Nanjing", "南京保利大剧院 Poly Grand Theatre, Nanjing"),
    ("蘇州文化藝術中心 大劇院", "Suzhou Culture & Arts Centre", "Suzhou", "苏州文化艺术中心 Suzhou Culture and Arts Centre"),
    ("蘇州灣大劇院 歌劇廳", "Suzhou Bay Grand Theatre", "Suzhou", "苏州湾大剧院 Suzhou Bay Grand Theatre"),
    ("無錫大劇院", "Wuxi Grand Theatre", "Wuxi", "无锡大剧院 Wuxi Grand Theatre"),
    ("常州大劇院", "Changzhou Grand Theatre", "Changzhou", "常州大剧院 Changzhou Grand Theatre"),
    ("南通大劇院", "Nantong Grand Theatre", "Nantong", "南通大剧院 Nantong Grand Theatre"),
    ("揚州運河大劇院", "Yangzhou Canal Grand Theatre", "Yangzhou", "扬州运河大剧院, Yangzhou"),
    ("昆山文化藝術中心 大劇場", "Kunshan Culture & Arts Centre", "Kunshan", "昆山文化艺术中心 Kunshan Culture and Arts Centre"),
    ("泰州大劇院", "Taizhou Grand Theatre", "Taizhou", "泰州大剧院 Taizhou Grand Theatre, Jiangsu"),
    ("連雲港大劇院", "Lianyungang Grand Theatre", "Lianyungang", "连云港大剧院 Lianyungang Grand Theatre"),
    # 浙江 Zhejiang
    ("杭州大劇院 歌劇院", "Hangzhou Grand Theatre", "Hangzhou", "杭州大剧院 Hangzhou Grand Theatre"),
    ("杭州運河大劇院", "Hangzhou Canal Grand Theatre", "Hangzhou", "杭州运河大剧院, Hangzhou"),
    ("寧波文化廣場大劇院", "Ningbo Culture Plaza Grand Theatre", "Ningbo", "宁波文化广场大剧院, Ningbo"),
    ("溫州大劇院", "Wenzhou Grand Theatre", "Wenzhou", "温州大剧院 Wenzhou Grand Theatre"),
    ("義烏文化廣場大劇院", "Yiwu Culture Square Grand Theatre", "Yiwu", "义乌文化广场大剧院, Yiwu"),
    ("紹興大劇院", "Shaoxing Grand Theatre", "Shaoxing", "绍兴大剧院 Shaoxing Grand Theatre"),
    # 山東 Shandong
    ("山東省會大劇院 歌劇廳", "Shandong Provincial Capital Grand Theatre", "Jinan", "山东省会大剧院, Jinan"),
    ("青島大劇院 歌劇廳", "Qingdao Grand Theatre", "Qingdao", "青岛大剧院 Qingdao Grand Theatre"),
    ("煙台大劇院", "Yantai Grand Theatre", "Yantai", "烟台大剧院 Yantai Grand Theatre"),
    ("臨沂大劇院", "Linyi Grand Theatre", "Linyi", "临沂大剧院 Linyi Grand Theatre"),
    ("濰坊大劇院", "Weifang Grand Theatre", "Weifang", "潍坊大剧院 Weifang Grand Theatre"),
    ("濟寧大劇院", "Jining Grand Theatre", "Jining", "济宁大剧院 Jining Grand Theatre"),
    # 安徽/江西/福建
    ("合肥大劇院 歌劇廳", "Hefei Grand Theatre", "Hefei", "合肥大剧院 Hefei Grand Theatre"),
    ("蕪湖大劇院", "Wuhu Grand Theatre", "Wuhu", "芜湖大剧院 Wuhu Grand Theatre"),
    ("江西藝術中心 大劇場", "Jiangxi Arts Centre", "Nanchang", "江西艺术中心 Jiangxi Arts Centre, Nanchang"),
    ("海峽文化藝術中心 歌劇廳", "Strait Culture & Art Centre", "Fuzhou", "海峡文化艺术中心 Strait Culture and Art Centre, Fuzhou"),
    ("廈門閩南大戲院", "Xiamen Minnan Grand Theatre", "Xiamen", "厦门闽南大戏院 Minnan Grand Theatre, Xiamen"),
    ("廈門滄江劇院", "Xiamen Cangjiang Theatre", "Xiamen", "厦门沧江剧院, Xiamen"),
    # 廣東 Guangdong
    ("廣州大劇院 歌劇廳", "Guangzhou Opera House", "Guangzhou", "广州大剧院 Guangzhou Opera House"),
    ("廣州保利大劇院", "Guangzhou Poly Grand Theatre", "Guangzhou", "广州保利大剧院 Poly Grand Theatre, Guangzhou"),
    ("深圳保利劇院", "Shenzhen Poly Theatre", "Shenzhen", "深圳保利剧院 Poly Theatre, Shenzhen"),
    ("深圳濱海藝術中心 歌劇廳", "Shenzhen Bay Arts Center", "Shenzhen", "深圳滨海艺术中心, Shenzhen"),
    ("深圳光明文化藝術中心 大劇場", "Shenzhen Guangming Culture & Arts Center", "Shenzhen", "深圳光明文化艺术中心, Shenzhen"),
    ("深圳坪山大劇院", "Shenzhen Pingshan Grand Theatre", "Shenzhen", "深圳坪山大剧院, Shenzhen"),
    ("東莞玉蘭大劇院", "Dongguan Yulan Grand Theatre", "Dongguan", "东莞玉兰大剧院 Yulan Grand Theatre, Dongguan"),
    ("珠海大劇院", "Zhuhai Grand Theatre", "Zhuhai", "珠海大剧院 Zhuhai Grand Theatre"),
    ("佛山大劇院", "Foshan Grand Theatre", "Foshan", "佛山大剧院 Foshan Grand Theatre, Shunde"),
    ("佛山瓊花大劇院", "Foshan Qionghua Grand Theatre", "Foshan", "佛山琼花大剧院, Foshan"),
    ("惠州大劇院", "Huizhou Grand Theatre", "Huizhou", "惠州大剧院 Huizhou Grand Theatre"),
    ("中山文化藝術中心 大劇場", "Zhongshan Culture & Arts Centre", "Zhongshan", "中山文化艺术中心 Zhongshan, Guangdong"),
    # 廣西/海南
    ("廣西文化藝術中心 歌劇廳", "Guangxi Culture & Arts Centre", "Nanning", "广西文化艺术中心 Guangxi Culture and Arts Centre, Nanning"),
    ("海南省歌舞劇院", "Hainan Opera & Dance Theatre", "Haikou", "海南省歌舞剧院, Haikou"),
    ("海口灣演藝中心", "Haikou Bay Performing Arts Center", "Haikou", "海口湾演艺中心, Haikou"),
    # 湖北/湖南
    ("武漢琴台大劇院", "Wuhan Qintai Grand Theatre", "Wuhan", "武汉琴台大剧院 Qintai Grand Theatre, Wuhan"),
    ("武漢劇院", "Wuhan Theatre", "Wuhan", "武汉剧院 Wuhan Theatre"),
    ("長沙梅溪湖國際文化藝術中心 大劇場", "Changsha Meixihu Intl Culture & Art Centre", "Changsha", "长沙梅溪湖国际文化艺术中心 Meixihu, Changsha"),
    ("湖南大劇院", "Hunan Grand Theatre", "Changsha", "湖南大剧院 Hunan Grand Theatre, Changsha"),
    ("株洲神農大劇院", "Zhuzhou Shennong Grand Theatre", "Zhuzhou", "株洲神农大剧院, Zhuzhou"),
    ("衡陽神農大劇院", "Hengyang Shennong Grand Theatre", "Hengyang", "衡阳神农大剧院, Hengyang"),
    # 河南/河北/山西/內蒙古
    ("河南藝術中心 大劇場", "Henan Art Center", "Zhengzhou", "河南艺术中心 Henan Art Center, Zhengzhou"),
    ("河北藝術中心 大劇場", "Hebei Art Center", "Shijiazhuang", "河北艺术中心, Shijiazhuang"),
    ("石家莊大劇院 大劇場", "Shijiazhuang Grand Theatre", "Shijiazhuang", "石家庄大剧院 Shijiazhuang Grand Theatre"),
    ("山西大劇院 歌劇廳", "Shanxi Grand Theatre", "Taiyuan", "山西大剧院 Shanxi Grand Theatre, Taiyuan"),
    ("烏蘭恰特大劇院", "Ulanqab Grand Theatre (Hohhot)", "Hohhot", "乌兰恰特大剧院 Hohhot, Inner Mongolia"),
    # 四川/貴州/雲南
    ("成都城市音樂廳 歌劇廳", "Chengdu City Concert Hall", "Chengdu", "成都城市音乐厅 Chengdu City Concert Hall"),
    ("四川大劇院 大劇場", "Sichuan Grand Theatre", "Chengdu", "四川大剧院 Sichuan Grand Theatre, Chengdu"),
    ("成都高新中演大劇院", "Chengdu Hi-tech Zhongyan Grand Theatre", "Chengdu", "成都高新中演大剧院, Chengdu"),
    ("貴陽大劇院", "Guiyang Grand Theatre", "Guiyang", "贵阳大剧院 Guiyang Grand Theatre"),
    ("雲南大劇院 歌劇廳", "Yunnan Grand Theatre", "Kunming", "云南大剧院 Yunnan Grand Theatre, Kunming"),
    # 陝西/甘肅/寧夏/青海/新疆
    ("陝西大劇院 歌劇廳", "Shaanxi Grand Theatre", "Xi'an", "陕西大剧院 Shaanxi Grand Theatre, Xi'an"),
    ("西安大明宮保利大劇院", "Xi'an Daminggong Poly Grand Theatre", "Xi'an", "西安大明宫保利大剧院, Xi'an"),
    ("西安人民劇院", "Xi'an People's Theatre", "Xi'an", "西安人民剧院 Xi'an People's Theatre"),
    ("甘肅大劇院 大劇場", "Gansu Grand Theatre", "Lanzhou", "甘肃大剧院 Gansu Grand Theatre, Lanzhou"),
    ("寧夏人民劇院", "Ningxia People's Theatre", "Yinchuan", "宁夏人民剧院 Ningxia People's Theatre, Yinchuan"),
    ("青海大劇院 歌劇廳", "Qinghai Grand Theatre", "Xining", "青海大剧院 Qinghai Grand Theatre, Xining"),
    ("新疆藝術劇院", "Xinjiang Art Theatre", "Urumqi", "新疆艺术剧院 Xinjiang Art Theatre, Urumqi"),
    # 東北 Northeast
    ("盛京大劇院 歌劇廳", "Shengjing Grand Theatre", "Shenyang", "盛京大剧院 Shengjing Grand Theatre, Shenyang"),
    ("大連國際會議中心大劇院", "Dalian Intl Conference Center Grand Theatre", "Dalian", "大连国际会议中心大剧院, Dalian"),
    ("長春市文化廣場大劇院", "Changchun Culture Square Grand Theatre", "Changchun", "长春文化广场大剧院, Changchun"),
    ("長影音樂廳", "Changying Concert Hall", "Changchun", "长影音乐厅 Changying Music Hall, Changchun"),
    ("哈爾濱大劇院 歌劇廳", "Harbin Grand Theatre", "Harbin", "哈尔滨大剧院 Harbin Grand Theatre"),
    ("大慶歌劇院", "Daqing Opera House", "Daqing", "大庆歌剧院 Daqing Opera House"),
]


def main():
    key = gg.load_key()
    force = "--all" in sys.argv
    out_path = DATA / "cn_venues.json"
    existing = {v["native"]: v for v in json.loads(out_path.read_text(encoding="utf-8"))} if out_path.exists() else {}

    out = []
    print(f"geocoding {len(VENUES)} China venues", flush=True)
    for i, (native, en, city, query) in enumerate(VENUES, 1):
        if not force and native in existing and existing[native].get("lat"):
            out.append(existing[native]); continue
        r = gg.places_new(query, key)
        time.sleep(0.08)
        if isinstance(r, tuple) and r and r[0] != "DENIED" and len(r) >= 5:
            lat, lng = round(r[0], 6), round(r[1], 6)
            rec = {"native": native, "en": en, "city": city, "country": "China", "lat": lat, "lng": lng}
            print(f"  [{i}/{len(VENUES)}] {native} / {en} @ {lat},{lng}", flush=True)
        else:
            rec = {"native": native, "en": en, "city": city, "country": "China", "lat": None, "lng": None}
            print(f"  [{i}/{len(VENUES)}] {native} → NO RESULT (manual)", flush=True)
        out.append(rec)

    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for v in out if v.get("lat"))
    print(f"\nDONE: {ok}/{len(out)} geocoded -> data/cn_venues.json", flush=True)


if __name__ == "__main__":
    main()
