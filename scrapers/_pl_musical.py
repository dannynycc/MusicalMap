# -*- coding: utf-8 -*-
"""波蘭來源共用的「這齣是不是音樂劇」判定。

2026-09-02 從 `poland.py` 抽出來,給 `poland.py`(eBilet)與 `poland_teatry.py`
(劇院官網)共用。抽出來的兩個理由:

1. **規則不能分岔。** 同一齣戲在 eBilet 被判音樂劇、在劇院官網被判不是,
   會產生「同劇兩組」或「時有時無」這種最難查的資料錯。
2. **避免 import 副作用。** `poland.py` 在 module 層改 `sys.stdout`,
   別的腳本 `from poland import is_musical` 會連帶被改掉輸出串流
   (實測會炸「I/O operation on closed file」)。判定邏輯放在這裡就沒有副作用。

⚠️ `is_musical()` 回傳的是 **(keep, reason) 三態**,不是 bool:
      True  → 有明確的音樂劇訊號
      False → 有明確的非音樂劇訊號
      None  → 兩邊都沒訊號(不確定)
   直接寫 `if is_musical(t)` 永遠為真(非空 tuple),過濾器會【靜默失效】。
   呼叫端一定要解包,並自己決定 None 要算哪一邊:
     · eBilet:來源本身已經是「musicale」分類,None 傾向保留。
     · 劇院官網:節目表混雜演唱會/禮券/兒童劇,None 仍保留但靠 DROP 清單擋
       (這些劇院本來就是音樂劇院,劇名沒訊號的多半仍是自製音樂劇)。
"""

DROP_WORDS = [
    "koncert", "recital", "jazz", "kolęd", "koled", "kabaret", "stand-up",
    "stand up", "komediowy", "komediowa", "gala", "talent show", " tour",
    "tribute", "symfonicz", "improwizowany", "improwizacja",
]

# Known solo artists whose "musicale"-bucket entries are live shows, not musicals.
DROP_ARTISTS = [
    "michał bajor", "michal bajor", "edyta geppert", "igor herbut",
    "grzegorz turnau", "kayah", "andrzej piaseczny",
]

# Strong KEEP signals — overrides the drop list (e.g. a title that contains both
# "musical" and a borderline word). Known musical/operetka titles + genre words.
KEEP_WORDS = [
    "musical", "musicalow", "operetka", "wicked", "six", "mamma mia",
    "skrzypek na dachu", "dracula", "beetlejuice", "madagaskar",
    "next to normal", "metro", "dzień świstaka", "dzien swistaka",
    "chłopi", "chlopi", "wiedźmin", "wiedzmin", "producenci", "high heels",
    "my fair lady", "polita",
]

# 劇院官網節目表才會出現的非演出項目(eBilet 的 musicale 分類不會有)。
# 只給 poland_teatry.py 用,不影響 eBilet 那條路徑的既有行為。
VENUE_ONLY_DROP = [
    "voucher", "bon podarunkowy", "karta podarunkowa", "bilet podarunkowy",
    "zwiedzanie", "warsztat", "spotkanie", "wystawa", "casting", "próba otwarta",
    # 外語【客座】演出:這些劇院會把外國巡演團的校園場次排進自己的節目表,
    # 但那既不是他們的製作、常常也不是音樂劇。2026-09-02 實例:Buffo 節目表上的
    # 「GULLIVER´s TRAVELS - spektakl w języku angielskim」是 TNT Theatre Britain
    # 的英語巡演【話劇】,而且實際演出地點是 Teatr V6 不是 Buffo ——
    # 收進來會同時錯在「不是音樂劇」與「標錯場館座標」兩件事。
    # ⚠️ 代價:若這幾間真的接了英語音樂劇巡演,這條規則也會濾掉。
    #    可接受——那種情況 eBilet 那條路徑仍會收到(它是以節目為單位、不綁場館)。
    "w języku angielskim", "w jezyku angielskim", "w języku ukraińskim",
]


def is_musical(title):
    """Return (keep: bool|None, reason: str). KEEP words win over DROP words."""
    t = title.lower()
    if any(k in t for k in KEEP_WORDS):
        return True, "keep-signal"
    for a in DROP_ARTISTS:
        if a in t:
            return False, f"solo-artist ({a})"
    for w in DROP_WORDS:
        if w in t:
            return False, f"non-musical word ({w.strip()})"
    return None, "unsure"   # None = no strong signal either way


def keep_for_venue_site(title):
    """劇院官網用的判定:三態解包 + 額外擋掉節目表裡的非演出項目。

    回傳 True 才收。與 `is_musical()` 的差別只在多一層 VENUE_ONLY_DROP,
    以及把 None(不確定)當成保留 —— 這三間都是音樂劇院。"""
    t = title.lower()
    if any(w in t for w in VENUE_ONLY_DROP):
        return False
    keep, _ = is_musical(title)
    return keep is not False
