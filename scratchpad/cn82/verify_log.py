# -*- coding: utf-8 -*-
"""§3 查證紀錄:每組每語言一筆,記【判定 + 依據 + 要改什麼】。

為什麼要獨立檔:69 組 × 三語 = 200 多篇,邊讀邊記在腦子裡一定會漏;
而且「我看過了」與「我看過而且判定 OK」必須分得開 —— 沒有紀錄就等於沒查。

欄位:
  verdict  ok | fix | reject      (fix=大致對但要改;reject=整篇不能用)
  basis    憑什麼這樣判(對照了什麼)
  todo     具體要改什麼(給重生成或手動修用)
用法: 由我在對話裡呼叫 add() 寫入,或直接編輯 verify_log.json
"""
import io
import json
import os
import sys

# 🚨 不要在這裡包 sys.stdout —— 這支會被別的腳本 import,包了會讓呼叫端的 stdout 被關掉
P = "scratchpad/cn82/verify_log.json"


def load():
    return json.load(io.open(P, encoding="utf-8")) if os.path.exists(P) else {}


def add(group, lang, verdict, basis, todo=""):
    d = load()
    d.setdefault(group, {})[lang] = {"verdict": verdict, "basis": basis, "todo": todo}
    json.dump(d, io.open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


def summary():
    d = load()
    # 🚨 底線開頭的鍵是【註記】(例如 _overturned_suspicions),不是「某組某語的判定」,
    #    值也不是 {verdict,basis,todo} 的形狀。不排除掉會在 v["verdict"] 當場炸掉。
    d = {k: v for k, v in d.items() if not k.startswith("_")}
    from collections import Counter
    c = Counter(v["verdict"] for g in d.values() for v in g.values())
    print("查證紀錄:%d 組 / %d 篇 %s" % (len(d), sum(len(g) for g in d.values()), dict(c)))
    for g, langs in d.items():
        for lang, v in langs.items():
            if v["verdict"] != "ok":
                print("  %-22s %-8s %-6s %s" % (g[:22], lang, v["verdict"], v["todo"][:70]))


if __name__ == "__main__":
    summary()
