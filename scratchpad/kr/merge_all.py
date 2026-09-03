# -*- coding: utf-8 -*-
"""把三輪重生成的結果併回主輸出檔,並做入庫前的最後把關。

為什麼重寫(2026-09-03):原本的 merge_regen.py 用 list.json 的 prompt 字串回查主批,
但重生成 prompt 與主批不同,對回去很脆弱。實測 out_en/out_zht/out_zhs 三個檔
與 syn_todo.json 是【逐筆索引對齊】的,所以改用 code → 索引 直接寫入,不再靠字串比對。

三輪的由來:
  R1 主批判定「寫成別的戲」的 13 齣(依語言拆成 en 7 / zht 10 / zhs 8)
  R2 R1 沒排到、但逐句人工比對後同樣不合格的語言(en 3 / zhs 3)
  R3 人工通讀時新查出的:청사초롱(憑空五名員工)、파랑새(生病的是미틸不是仙女的女兒)、
     오싹한 알바(帳本角色欄重錄後重建 prompt)、his story 簡中(整個敘事框架寫錯)

把關項目(不通過不入庫):
  ① 非空 ② 中文正文不得殘留韓文(Club 설화 為劇名例外) ③ 不得殘留來源名/UI
  ④ 不得殘留後設句 ⑤ 字數落在區間 ⑥ 英文不得殘留韓文
"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "scratchpad/kr"
MAIN = {"en": "out_en.json", "zh": "out_zht.json", "cn": "out_zhs.json"}
LIM = {"en": (220, 340), "zh": (400, 450), "cn": (400, 450)}

C = {  # 便於閱讀的代號
    "hair": "26011256", "million": "26010134", "malhaji": "26009297",
    "exupery": "26011959", "hunky": "25003978", "cheong": "26009512",
    "parang": "26012302", "alba": "26003190", "hisstory": "26011932",
}
# (檔名, 該檔逐筆對應的 code)
JOBS = {
    "en": [("regen_en.json", None),
           ("regen2_en.json", [C["hair"], C["million"], C["malhaji"]]),
           ("regen3_en.json", [C["cheong"], C["parang"], C["alba"]])],
    "zh": [("regen_zht.json", None),
           ("regen3_zht.json", [C["cheong"], C["parang"], C["alba"]])],
    "cn": [("regen_zhs.json", None),
           ("regen2_zhs.json", [C["hair"], C["exupery"], C["hunky"]]),
           ("regen3_zhs.json", [C["cheong"], C["parang"], C["alba"], C["hisstory"]])],
}
CODES1 = {"en": "regen_en_codes.json", "zh": "regen_zht_codes.json", "cn": "regen_zhs_codes.json"}


def must(p):
    """一定要存在的檔;讀不到就讓它炸,不要靜默往下跑。"""
    return json.load(io.open("%s/%s" % (BASE, p), encoding="utf-8"))


def load(p, default=None):
    try:
        return must(p)
    except Exception:                                        # noqa: BLE001
        return default


def main():
    todo = must("syn_todo.json")
    c2i = {r["code"]: i for i, r in enumerate(todo)}
    log = must("verify_log.json")["shows"]
    rejected = {c for c, v in log.items() if v.get("verdict") == "reject"}
    merged = 0
    for lang, fn in MAIN.items():
        rows = must(fn)
        assert len(rows) == len(todo), (lang, len(rows), len(todo))
        for rf, codes in JOBS[lang]:
            reg = load(rf)
            if reg is None:
                print("  · %s 尚未產出,略過" % rf); continue
            if codes is None:
                codes = load(CODES1[lang], [])
            for i, r in enumerate(reg):
                if i >= len(codes):
                    print("  ✗ %s 第 %d 筆沒有對應 code" % (rf, i)); continue
                s = (r.get("synopsis") or "").strip()
                if not s:
                    print("  ✗ %s/%s 重生成是空的,保留原稿" % (rf, codes[i])); continue
                rows[c2i[codes[i]]]["synopsis"] = s
                rows[c2i[codes[i]]]["_regen"] = rf
                merged += 1
        for r in rows:
            r["size"] = len(r["synopsis"].split()) if lang == "en" \
                else len(r["synopsis"].replace("\n", "").replace(" ", ""))
        json.dump(rows, io.open("%s/%s" % (BASE, fn), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    print("併回主批:%d 篇" % merged)

    # ---- 把關(跳過 4 齣 reject) ----
    bad = 0
    han = re.compile(r"[가-힣]")
    meta = ["演出資訊", "公开演出资料", "公開演出資料", "官方剧情梗概", "官方劇情梗概",
            "資料來源", "资料来源", "版本比對", "版本比对", "以上为", "以上為",
            "根據官方", "根据官方", "本劇改編自官方", "官方文案"]
    src = re.compile(r"^\s*[a-z0-9][a-z0-9.\-]*\.[a-z][a-z0-9]{1,}\s*$", re.I | re.M)
    for lang, fn in MAIN.items():
        lo, hi = LIM[lang]
        for i, r in enumerate(must(fn)):
            if todo[i]["code"] in rejected:
                continue
            s = (r.get("synopsis") or "").strip()
            tag = "%s[%d] %s" % (lang, i, (todo[i].get("ko") or "")[:26])
            if not s:
                print("  ⚠ 空白 %s" % tag); bad += 1; continue
            n = len(s.split()) if lang == "en" else len(s.replace("\n", "").replace(" ", ""))
            if not (lo <= n <= hi):
                print("  ⚠ 字數 %d(區間 %d~%d) %s" % (n, lo, hi, tag)); bad += 1
            if han.search(s) and not (lang != "en" and han.findall(s) == list("설화")):
                print("  ⚠ 殘留韓文『%s』 %s" % ("".join(han.findall(s))[:12], tag)); bad += 1
            if src.search(s):
                print("  ⚠ 來源名殘留 %s" % tag); bad += 1
            for m in meta:
                if m in s:
                    print("  ⚠ 後設句『%s』 %s" % (m, tag)); bad += 1; break
    print("把關結果:%s" % ("全部通過 ✅" if bad == 0 else "%d 項待處理" % bad))
    return 0


raise SystemExit(main())
