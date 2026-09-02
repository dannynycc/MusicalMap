# -*- coding: utf-8 -*-
"""對【正式站】的資料重算覆蓋率,確認與本機一致。"""
import io, sys, json, re, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap-coverage"}
B = "https://themusicalmap.com/data/"
def get(u):
    with urllib.request.urlopen(urllib.request.Request(B+u, headers=UA), timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))
NONLAT = re.compile(r'[一-鿿㐀-䶿぀-ヿ가-힯ᄀ-ᇿ]')
HAN = re.compile(r'[一-鿿㐀-䶿]'); KANA = re.compile(r'[぀-ヿ]'); HG = re.compile(r'[가-힯ᄀ-ᇿ]')
ZH = {"中國","臺灣","台灣","香港","澳門","新加坡","China","Taiwan","Hong Kong","Macau","Singapore"}
en = get("variants/shows.en.json")["shows"]
ht = get("variants/shows.zh-hant.json")["shows"]
hs = get("variants/shows.zh-hans.json")["shows"]
syn = {}
for lg, sub in (("en","en"),("zh-hant","zh"),("zh-hans","zh-hans")):
    d = get("synopses/%s.json" % lg); d = d.get("syn", d)
    syn[lg] = set(g for g,v in d.items() if (v or {}).get(sub))
per = {}
for rows, lg in ((en,"en"),(ht,"zh-hant"),(hs,"zh-hans")):
    for r in rows:
        g = r.get("group")
        if not g: continue
        e = per.setdefault(g, {"t":{}, "a":{}, "c":set()})
        e["t"][lg] = r.get("title") or ""; e["a"][lg] = r.get("cn_annot") or ""
        e["c"].add(r.get("country") or "")
tot = len(per)
def zh_ok(e, lg):
    if e["a"].get(lg): return True
    t = e["t"].get(lg,"")
    return bool(HAN.search(t)) and not KANA.search(t) and not HG.search(t) and bool(e["c"] & ZH)
res = {}
res["title_en"] = sum(1 for e in per.values() if not NONLAT.search(e["t"]["en"]))
res["title_hant"] = sum(1 for e in per.values() if zh_ok(e,"zh-hant"))
res["title_hans"] = sum(1 for e in per.values() if zh_ok(e,"zh-hans"))
for lg in ("en","zh-hant","zh-hans"):
    res["syn_"+lg] = sum(1 for g in per if g in syn[lg])
print("正式站組數 %d" % tot)
for k,v in res.items():
    print("  %-12s %4d  = %5.1f%%" % (k, v, 100.0*v/tot))
