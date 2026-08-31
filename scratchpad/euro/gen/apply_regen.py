# -*- coding: utf-8 -*-
"""把重生成結果(regen_*.json)回填到 out_zht/out_zhs.json。

重生成時為了消歧義,prompt 用了「加強身份釘定」的字串(只補製作方/劇院/創作者/依據作品,
不含劇情),與原檔的 show key 不同,所以必須靠 regen_keymap.json 對回原始 key。
每一筆都必須對到唯一一筆,對不到就報錯——不默默跳過。
"""
import json, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
km = json.load(open(os.path.join(HERE, "regen_keymap.json"), encoding="utf-8"))

rc = 0
for lang, out_file, regen_file in (("zht", "out_zht.json", "regen_zht.json"),
                                   ("zhs", "out_zhs.json", "regen_zhs.json")):
    rp = os.path.join(HERE, regen_file)
    if not os.path.exists(rp):
        print("[skip] %s 尚未產生" % regen_file); continue
    regen = json.load(open(rp, encoding="utf-8"))
    orig_keys = km[lang]
    if len(regen) != len(orig_keys):
        print("[!] %s: 重生成 %d 筆,預期 %d 筆" % (regen_file, len(regen), len(orig_keys)))
        rc = 1
    out = json.load(open(os.path.join(HERE, out_file), encoding="utf-8"))
    idx = {r["show"]: r for r in out}
    done = 0
    for i, r in enumerate(regen):
        if i >= len(orig_keys):
            print("  [!] 第 %d 筆無對應原始 key" % (i + 1)); rc = 1; continue
        key = orig_keys[i]
        if key not in idx:
            print("  [!] 原始 key 不在 %s: %r" % (out_file, key[:60])); rc = 1; continue
        old = idx[key]["synopsis"]
        idx[key]["synopsis"] = r["synopsis"]
        done += 1
        print("  [ok] %-52s %d字 → %d字" % (key[:52], len(old), len(r["synopsis"])))
    json.dump(out, open(os.path.join(HERE, out_file), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("%s: 回填 %d 筆" % (out_file, done))
sys.exit(rc)
