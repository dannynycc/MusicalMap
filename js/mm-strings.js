/* mm-strings.js — 足跡側(u.html,之後 me.html)的 UI 字典與語言解析。
   語言決定順序:?hl= 參數(en|zh-hant|zh-hans) → Worker 注入的 window.MM_HL → navigator.language → zh-hant。
   語言必須進網址(?hl=)才能被搜尋引擎分語言收錄(Google 官方指引 + Strava/X 實務,
   見 docs/DESIGN_username_sharing.md);navigator 只是給「沒帶參數的真人」的禮貌預設。
   zh-hans:P1 暫用 zh-hant 字典顯示(未接 OpenCC;主站 chrome 已有此機制,之後統一)。 */
(function () {
  var STR = {
    'zh-hant': {
      // ---- u.html 靜態 ----
      nav_theatres: '所有劇院', nav_map: '地圖首頁', nav_guide: '使用說明', nav_create: '＋ 建立你自己的',
      nav_privacy: '隱私權政策', nav_terms: '使用條款',
      th_midnight: '午夜（暗）', th_gallery: '畫廊白（亮）', th_cream: '節目單奶油（亮）', th_neon: '霓虹（暗）', th_deco: '裝飾金（暗）',
      aria_theme: '主題底色', aria_seg: '檢視模式', aria_sort: '排序', aria_close: '關閉',
      hero_sub: '每看一場，蓋一個章',
      seg_poster: '海報牆', seg_passport: '護照', seg_log: '清單',
      sort_date: '最近觀看', sort_rating: '評分', sort_count: '次數', sort_title: '劇名',
      sec_map: '我的觀劇足跡', sec_map_hint: '點一座城市，只看那裡的收藏',
      aria_zoom_in: '放大', aria_zoom_out: '縮小', aria_zoom_reset: '重置',
      map_hint: '滾輪縮放 · 拖曳平移',
      legend_dot: '圓點 = 看過音樂劇的城市', legend_size: '圓大小 = 看的場數',
      sec_stats: '觀劇統計',
      st_shows: '🎭 最常看的劇', st_countries: '🌏 最常去的國家', st_cities: '🏙 最常去的城市', st_theatres: '🏛 最常去的劇院',
      st_year: '📅 各年', st_month: '📅 各月', st_week: '📅 各星期',
      sec_you: '關於這位劇迷', badges_title: '🏅 成就徽章',
      footer_1: '海報牆與護照，是同一批收藏的兩種看法。',
      footer_2: '封面取自各劇官方與公開資料。想擁有自己的音樂劇護照？',
      footer_cta: '建立你自己的 →',
      empty_title: '找不到這個公開頁', empty_sub: '這個收藏頁不存在，或擁有者尚未公開。',
      empty_cta: '＋ 建立你自己的 My Musicals',
      dt_zoom: '↗ 點圖開新分頁看原圖',
      // ---- u-view.js runtime ----
      bn_musicals: '音樂劇 Musicals', bn_unique: '不同作品 Unique', bn_cities: '城市 Cities', bn_countries: '國家 Countries',
      newest_label: '最新一場', none_yet: '還沒看過任何一場',
      upcoming_dot_n: '· 即將 {n} 場', upcoming_n: '即將 {n} 場',
      chip_all: '全部', ribbon_upcoming: '即將上演', up_mark: '即將<br>上演', up_suffix: '（即將上演）', detail_suffix: ' 詳情',
      n_musicals: '{n} 部音樂劇',
      lt_show: '劇目', lt_city: '城市', lt_date: '日期', lt_rate: '評分', lt_tbd: '未定',
      date_tbd: '日期未定',
      pin_aria: '{city} · {n} 部音樂劇',
      citylist_title: '造訪城市 Cities', citylist_sub: '{c} 座城市 · {k} 國 · 共 {t} 場',
      badge_shows: '{n} 場演出', badge_countries: '{n} 國蓋章', badge_cities: '{n} 座城市',
      badge_unique: '{n} 部不同作品', badge_fav: '{n} 部最愛',
      persona_title: '你是什麼樣的劇迷？',
      dt_venue: '劇院', dt_city: '城市', dt_date: '日期', dt_time: '時間', dt_seat: '座位', dt_price: '票價', dt_link: '連結', dt_open_link: '開啟連結',
      h1_suffix: '{name} 的音樂劇收藏',
      // ---- data.js personality(me/u 共用) ----
      p_G: '環球旅人', p_L: '在地常客', p_Y: '念舊死忠', p_X: '嚐鮮探索',
      p_M: '當代派', p_C: '經典派', p_S: '大製作控', p_I: '小劇場魂',
      p_n_countries: '{n} 國', p_repeat: '重看率 {n}%',
      p_blurb_globe: '你橫跨 {n} 國追劇', p_blurb_local_country: '你在 {n} 個國家看過戲', p_blurb_local_place: '你在 {n} 個地方看過戲',
      p_blurb_loyal: '願意為愛的戲二刷三刷', p_blurb_fresh: '幾乎每齣都嚐鮮',
      p_axis_era: '{m} 現代 / {c} 經典', p_axis_scale: '{s} 大 / {i} 小',
      p_blurb_modern: '口味偏當代', p_blurb_classic: '鍾情經典',
      p_blurb_spectacle: '也擋不住大製作的聲光', p_blurb_intimate: '更愛小劇場的親密',
      p_sep: '，', p_end: '。',
      // ---- me.html 專屬(登入頁,localStorage 記語言) ----
      gate_loading: '載入中…', gate_login: '使用 Google 登入',
      gate_signin: '<b style="font-size:26px">我的音樂劇</b><br><span style="opacity:.72;font-size:14.5px;font-weight:500">登入後，你看過的每一齣音樂劇都會存進你的帳號、跨裝置同步。</span>',
      gate_secure: '用你的 Google 帳戶安全登入。我們只讀取你的名稱與 email,不會代你張貼任何內容。',
      gate_syncing: '同步你的收藏中…', gate_no_backend: '⚠ 後端尚未設定',
      gate_load_fail: '讀取收藏失敗，請重新整理。',
      gate_preview: '登入後長這樣——你的海報牆、觀劇護照與觀劇統計，全部自動生成：',
      gate_browse_map: '先逛演出地圖 →', gate_see_guide: '看使用說明 →',
      nav_share: '分享', nav_logout: '登出', me_hero_title: '我的音樂劇收藏',
      demo_banner_b: '👋 這是範例收藏', demo_banner_rest: ' —— 先讓你看看蓋滿章後的樣子。按右邊加入你第一齣看過的劇，整頁就換成你自己的。',
      demo_cta: '＋ 加入第一齣音樂劇', demo_sub: '範例預覽 · 加入後就換成你的',
      footer2_me: '封面取自各劇官方與公開資料；目前顯示的是範例紀錄，登入後就換成你自己的。',
      edit_this: '編輯這齣', delete_this: '刪除這齣', edit: '編輯', delete: '刪除',
      first_west_end: 'FIRST WEST END', first_broadway: 'FIRST BROADWAY', first: 'FIRST',
      fab_add: '＋ 加入音樂劇', log_title: '加入音樂劇', lt_undated: '未定',
      share_title: '分享我的收藏', share_lead: '把看過的每一齣音樂劇分享給朋友。',
      share_url_label: '你的專屬網址',
      handle_to_acct_1: '網址名稱是你的帳號身份，要更改請到 ', handle_to_acct_link: '帳號設定', handle_to_acct_2: '。',
      handle_input_label: '網址名稱（英文、數字、底線或連字號，1–30 字）',
      pub_public: '公開我的收藏頁', pub_public_sub: '關閉時，就算有連結別人也看不到你的收藏。',
      sfg_title: '公開頁要顯示哪些敏感資訊？',
      show_price: '顯示票價', show_seat: '顯示座位', note_never: '筆記永遠不會出現在公開頁。',
      copy: '複製', copied: '已複製！', later: '之後再說', save: '儲存', saving: '儲存中…',
      acct_title: '帳號設定',
      acct_lead: '網址名稱是你的帳號身份。更改後舊網址會自動轉到新網址，已分享出去的連結不會壞；舊名稱會永久保留給你，別人拿不走。',
      acct_handle_label: '網址名稱 username', acct_display_label: '顯示名稱（公開頁的標題）', cancel: '取消',
      onb_title: '歡迎！取一個你的網址名稱',
      onb_lead: '這是你的帳號身份，也是公開分享網址的一部分。之後可在「帳號設定」更改，舊網址會自動轉到新的。', logout: '登出',
      h_input_hint: '輸入英文、數字、底線或連字號（1–30 字）。', h_reserved: '這個名稱是保留字，換一個。',
      h_current: '這是你目前的網址。', h_checking: '檢查中…',
      h_avail: '✓ {h} 可以用！', h_taken: '✗ {h} 已被使用，換一個。', h_will_check: '儲存時會確認是否重複。',
      h_taken_short: '✗ 已被使用，換一個。', h_bad_format: '只能用英文、數字、底線、連字號（1–30 字）。',
      h_save_fail: '儲存失敗：', chips_tip: '可用的建議：', onb_done: '✓ 完成！',
      url_empty: '先取一個網址名稱。', acct_url_empty: '網址名稱不能空白。',
      saved_redirect: '✓ 已儲存。舊網址會自動轉到新網址。', display_save_fail: '顯示名稱儲存失敗：',
      confirm_delete: '確定要刪除《{name}》這筆紀錄嗎？\n(刪除後仍可從左下角「復原」救回)',
      this_show: '這齣', deleted: '已刪除《{name}》', undo: '復原',
      // ---- me-input.html 專屬(輸入表單,iframe) ----
      mi_h1: '記錄一齣音樂劇', mi_open_log: '＋ 記錄一齣音樂劇', mi_sheet_record: '記錄一齣音樂劇',
      mi_sec_records: '我的觀劇紀錄', mi_not_recorded: '尚未記錄', mi_add: '加入', mi_update: '更新',
      mi_footer_1: '搜尋→選製作→自動帶入→年份優先的日期→存檔蓋章。', mi_footer_2: '資料存在瀏覽器（localStorage）；海報為各劇真實封面。',
      mi_loading_lib: '載入劇庫中…',
      mi_search_ph: '打中文或英文劇名…例 歌劇魅影 / phantom', mi_search_hint: '搜尋你看過的音樂劇 —— 中文、英文都行，搜不到也能手動新增。',
      mi_no_result: '目錄裡找不到「{v}」', mi_manual_add: '＋ 手動新增（自己打劇名／城市）',
      mi_musical: '音樂劇', mi_manual_input_lbl: '手動輸入（目錄裡找不到的劇）', mi_manual_title: '手動新增',
      mi_back: '← 返回', mi_back_search: '← 返回搜尋', mi_back_prods: '← 返回版本', mi_back_pick_prod: '← 返回（選製作）',
      fld_title: '劇名', fld_title_req: '劇名 *', fld_city: '城市', fld_venue: '劇院', fld_venue_opt: '劇院（選填）',
      ph_city: '例 London / 台北', ph_venue: '例 臺中國家歌劇院', ph_title: '劇名',
      fld_date_opt: '哪一年・月・日看的（選填）', opt_year: '年', opt_month: '月', opt_day: '日',
      mi_month_n: '{n} 月', mi_day_n: '{n} 日',
      fld_time: '時間 Time（選填）', fld_rating: '評分 Rating（選填）', fld_seat: '座位 Seat', ph_seat: '例 Stalls A12 / 一樓 H23',
      fld_price: '票價 Price', ph_cur: '幣別 ▾', fld_note: '心得 Note', ph_note: '那一夜的記憶…',
      ds_hint: '填到「日」才能算星期幾、各月統計；只記得年份也沒關係，之後可再填。',
      ds_hint2: '填到「日」才能算星期幾、各月統計；只記得年份也行。',
      mgeo_hint: '打城市或劇院時會自動對上國家；對得上就能標在地圖。',
      geo_rematch: '改城市／劇院會重新對上國家座標；對不上仍會存文字。',
      geo_no_coord: '找不到座標時仍會存城市/劇院文字（地圖上可能不顯示）。',
      geo_matched: '對上 {c}', geo_matched_map: '對上 {c} · 會標在地圖',
      disclose_open: '＋ 加入細節（評分・座位・票價・心得）', disclose_close: '－ 收起細節',
      pick_prod: '你看的是哪一個製作？', prod_versions: '{n} 個版本', prod_tour: '巡演',
      prod_cities: '{n} 個城市 · {list}', prod_stations: '{n} 站',
      pick_none: '以上都不是 — 我看的是別的城市／年份', pick_none_sub: '自己填，劇名和海報幫你留著',
      pick_city_q: '{label} — 哪一個城市？', pick_city_none: '不記得是哪個城市', pick_city_none_sub: '先記下這個巡演，城市之後再填',
      run_playing: '本劇在 {city} 上演 {range}', run_recent: '近期在 {city} 上演',
      venue_city: '劇院・城市', edit_can_change: '編輯可改', when_seen: '什麼時候看的？', not_required: '非必填',
      star_n: '{n} 顆星', toast_updated: '✓ 已更新這筆紀錄', toast_stamped: '🎭 已蓋章！這是你的第 <b>{n}</b> 齣音樂劇',
      date_undated: '日期未定', mi_log_ct_n: '{n} 齣',
      recent_added: '這次加入的 · {n} 齣', recent_added_sub: '加錯了？點 ✎ 改、🗑 刪',
      recent_empty: '搜尋你看過的音樂劇 —— 中文、英文都行，搜不到也能手動新增。', recent_empty_sub: '加好的會即時長到海報牆與護照。',
      mi_edit_record: '編輯紀錄', mi_added: '已加入',
      added_one: '🎭 已加入「{name}」！', added_n: '🎭 已加入 <b>{n}</b> 齣！',
      batch_hint: '想記日期、評分嗎？點下面那齣就能填；不填也沒關係，回收藏後點海報卡右上角的 <b>✎</b> 隨時都能填。',
      date_later: '日期之後填', seat_label: '座位 <b>{v}</b>', price_label: '票價 <b>{v}</b>', edit_btn: '✎ 編輯',
      add_more: '＋ 再加入一齣', batch_done: '完成，回我的收藏 →',
      fld_poster: '自訂海報網址 Poster URL（選填）', ph_poster: '貼上圖片網址，覆蓋系統海報；清空即還原', poster_prev: '預覽',
      fld_link: '連結 / 售票網址 Link（選填）', ph_link: '貼上這場的售票或節目連結（選填）',
      mi_intro: '大多數人是在加入以前看過的劇（五年前那一齣），所以日期不預設今天——選了劇，系統用該製作的演出區間幫你回憶是哪一年；劇院／城市／海報全自動帶入，你幾乎不用打字。',
      mi_hint: '試試:打「歌劇魅影」或「phantom」或「les mis」。資料來自 MusicalMap 真實劇目庫。',
      mi_stamp_here: '蓋章<br>處', mi_empty_passport: '你的觀劇護照還是空白的。<br><b>按上面「＋ 記錄一齣音樂劇」</b>蓋下第一個印章。',
      // ---- how.html 使用說明頁 ----
      how_title: '使用說明 — MusicalMap',
      how_meta: 'MusicalMap 怎麼用：一張地圖看全世界正在上演的音樂劇，把你看過的每一齣記成一本觀劇護照，分享出去。',
      how_nav_start: '我的音樂劇', how_eyebrow: '使用說明',
      how_hero: '一張地圖，<br>看見全世界正在上演的<em>音樂劇</em>。',
      how_lede: '免登入就能探索此刻全球正在上演的音樂劇——百老匯、倫敦西區、各國巡演。登入之後，把你看過的都記成一本觀劇護照，分享出去。',
      how_cta_map: '探索演出地圖', how_cta_me: '建立我的觀劇護照',
      how_p1_h: '探索，不必註冊', how_p1_lede: '打開地圖，全球此刻正在上演的音樂劇一次看盡。想看哪一齣，直接連過去訂票。',
      how_a1_n: '在地圖上', how_a1_h: '每張海報，都是一齣正在上演的劇', how_a1_p: '地圖上的標記就是各劇的海報，靠近的會聚成一顆數字圓圈——數字是那一帶正在演的場數。點一張海報，看檔期、劇院與售票連結。',
      how_a2_n: '一鍵訂票', how_a2_h: '看到喜歡的，直接過去訂', how_a2_p: '每一齣都附售票連結，多數還有官方網站。我們不賣票——只把你帶到對的地方。',
      how_bridge: '看過的那些，別讓它們只留在記憶裡。',
      how_p2_h: '記下你看過的每一齣', how_p2_lede: '登入之後，你看過的劇會長成一面海報牆、一本蓋章護照，還有你的觀劇統計。全部自動生成。',
      how_b1_n: '加入一齣', how_b1_h: '搜劇名，其餘自動帶入', how_b1_p: '中英文搜尋都行，劇院、城市、海報自動補上。填看劇的日期、評分、座位、心得——只記得年份也沒關係。每看一場，護照上就多一個章。',
      how_b2_n: '你的觀劇統計', how_b2_h: '看久了，會浮現一個輪廓', how_b2_p: '最常看的劇、去過的城市與國家、各年各月的觀劇分布——不用自己算，一眼看出你是什麼樣的劇迷。',
      how_b3_n: '分享出去', how_b3_h: '你的專屬頁，一個網址就能分享', how_b3_p: '設一個網址名稱，就有一個公開頁能傳給朋友。票價、座位要不要公開由你決定；筆記永遠只有你看得到。',
      how_b4_n: '登入很單純', how_b4_h: '用 Google 登入，跨裝置同步', how_b4_p: '我們只讀你的名稱與 email，不會代你張貼任何內容。你的收藏存在帳號裡，換手機、換電腦都在。',
      how_final_h: '從哪裡開始都可以', how_final_p: '先逛地圖找靈感，或直接記下你看過的第一齣。', how_final_cta: '建立我的觀劇護照', how_final_cta2: '先探索地圖',
      how_footer: 'MusicalMap — 全球音樂劇即時地圖，與你的觀劇護照。', how_footer_link: '回到地圖',
    },
    'en': {
      nav_theatres: 'All Theatres', nav_map: 'Map home', nav_guide: 'Guide', nav_create: '＋ Create your own',
      nav_privacy: 'Privacy', nav_terms: 'Terms',
      th_midnight: 'Midnight (dark)', th_gallery: 'Gallery white (light)', th_cream: 'Playbill cream (light)', th_neon: 'Neon (dark)', th_deco: 'Deco gold (dark)',
      aria_theme: 'Theme', aria_seg: 'View mode', aria_sort: 'Sort', aria_close: 'Close',
      hero_sub: 'One stamp for every show you see',
      seg_poster: 'Posters', seg_passport: 'Passport', seg_log: 'List',
      sort_date: 'Recently seen', sort_rating: 'Rating', sort_count: 'Times seen', sort_title: 'Title',
      sec_map: 'Where I’ve been', sec_map_hint: 'Click a city to see only those shows',
      aria_zoom_in: 'Zoom in', aria_zoom_out: 'Zoom out', aria_zoom_reset: 'Reset',
      map_hint: 'Scroll to zoom · drag to pan',
      legend_dot: 'Dot = a city with shows seen', legend_size: 'Size = number of shows',
      sec_stats: 'Stats',
      st_shows: '🎭 Most-seen shows', st_countries: '🌏 Top countries', st_cities: '🏙 Top cities', st_theatres: '🏛 Top theatres',
      st_year: '📅 By year', st_month: '📅 By month', st_week: '📅 By weekday',
      sec_you: 'About this theatregoer', badges_title: '🏅 Badges',
      footer_1: 'The poster wall and the passport are two views of the same collection.',
      footer_2: 'Artwork comes from each show’s official and public sources. Want your own musical passport?',
      footer_cta: 'Create your own →',
      empty_title: 'This page doesn’t exist', empty_sub: 'It may have been removed, or the owner hasn’t made it public.',
      empty_cta: '＋ Create your own My Musicals',
      dt_zoom: '↗ Open full-size image in a new tab',
      bn_musicals: 'Musicals', bn_unique: 'Unique shows', bn_cities: 'Cities', bn_countries: 'Countries',
      newest_label: 'Latest', none_yet: 'No shows seen yet',
      upcoming_dot_n: '· {n} upcoming', upcoming_n: '{n} upcoming',
      chip_all: 'All', ribbon_upcoming: 'Coming up', up_mark: 'Coming<br>up', up_suffix: ' (upcoming)', detail_suffix: ' details',
      n_musicals: '{n} musicals',
      lt_show: 'Show', lt_city: 'City', lt_date: 'Date', lt_rate: 'Rating', lt_tbd: 'TBD',
      date_tbd: 'Date TBD',
      pin_aria: '{city} · {n} musicals',
      citylist_title: 'Cities visited', citylist_sub: '{c} cities · {k} countries · {t} shows',
      badge_shows: '{n} shows', badge_countries: '{n} countries stamped', badge_cities: '{n} cities',
      badge_unique: '{n} unique shows', badge_fav: '{n} favourites',
      persona_title: 'What kind of theatregoer are you?',
      dt_venue: 'Theatre', dt_city: 'City', dt_date: 'Date', dt_time: 'Time', dt_seat: 'Seat', dt_price: 'Price', dt_link: 'Link', dt_open_link: 'Open link',
      h1_suffix: '{name}’s Musicals',
      p_G: 'Globetrotter', p_L: 'Hometown regular', p_Y: 'Loyal rewatcher', p_X: 'Explorer',
      p_M: 'Modernist', p_C: 'Classicist', p_S: 'Spectacle lover', p_I: 'Small-stage soul',
      p_n_countries: '{n} countries', p_repeat: '{n}% rewatch rate',
      p_blurb_globe: 'You’ve chased shows across {n} countries', p_blurb_local_country: 'You’ve seen shows in {n} countries', p_blurb_local_place: 'You’ve seen shows in {n} place(s)',
      p_blurb_loyal: 'happy to see a beloved show two or three times', p_blurb_fresh: 'almost always trying something new',
      p_axis_era: '{m} modern / {c} classic', p_axis_scale: '{s} big / {i} small',
      p_blurb_modern: 'tastes lean contemporary', p_blurb_classic: 'devoted to the classics',
      p_blurb_spectacle: 'can’t resist a big spectacle', p_blurb_intimate: 'prefers the intimacy of a small stage',
      p_sep: ', ', p_end: '.',
      gate_loading: 'Loading…', gate_login: 'Sign in with Google',
      gate_signin: '<b style="font-size:26px">My Musicals</b><br><span style="opacity:.72;font-size:14.5px;font-weight:500">Sign in and every show you’ve seen is saved to your account and synced across devices.</span>',
      gate_secure: 'Secure sign-in with your Google account. We only read your name and email — we never post anything on your behalf.',
      gate_syncing: 'Syncing your collection…', gate_no_backend: '⚠ Backend not configured',
      gate_load_fail: 'Couldn’t load your collection. Please refresh.',
      gate_preview: 'After you sign in — your poster wall, theatre passport and stats, all generated automatically:',
      gate_browse_map: 'Browse the map first →', gate_see_guide: 'Read the guide →',
      nav_share: 'Share', nav_logout: 'Sign out', me_hero_title: 'My Musicals',
      demo_banner_b: '👋 This is a sample collection', demo_banner_rest: ' — a preview of what it looks like once stamped. Add your first show on the right and the whole page becomes yours.',
      demo_cta: '＋ Add your first musical', demo_sub: 'Sample preview · becomes yours once you add a show',
      footer2_me: 'Artwork comes from each show’s official and public sources. This is a sample for now — it becomes yours once you sign in.',
      edit_this: 'Edit this show', delete_this: 'Delete this show', edit: 'Edit', delete: 'Delete',
      first_west_end: 'FIRST WEST END', first_broadway: 'FIRST BROADWAY', first: 'FIRST',
      fab_add: '＋ Add a musical', log_title: 'Add a musical', lt_undated: 'TBD',
      share_title: 'Share my collection', share_lead: 'Share every musical you’ve seen with friends.',
      share_url_label: 'Your personal URL',
      handle_to_acct_1: 'Your URL name is your account identity. To change it, go to ', handle_to_acct_link: 'Account settings', handle_to_acct_2: '.',
      handle_input_label: 'URL name (letters, digits, underscore or hyphen, 1–30 chars)',
      pub_public: 'Make my collection public', pub_public_sub: 'When off, no one can see your collection even with the link.',
      sfg_title: 'Which sensitive details to show on the public page?',
      show_price: 'Show price', show_seat: 'Show seat', note_never: 'Notes never appear on the public page.',
      copy: 'Copy', copied: 'Copied!', later: 'Later', save: 'Save', saving: 'Saving…',
      acct_title: 'Account settings',
      acct_lead: 'Your URL name is your account identity. After you change it, the old URL redirects to the new one — links you’ve already shared won’t break; the old name stays reserved for you and no one else can take it.',
      acct_handle_label: 'URL name (username)', acct_display_label: 'Display name (the public page title)', cancel: 'Cancel',
      onb_title: 'Welcome! Pick your URL name',
      onb_lead: 'This is your account identity and part of your public share URL. You can change it later in Account settings — the old URL will redirect to the new one.', logout: 'Sign out',
      h_input_hint: 'Letters, digits, underscore or hyphen (1–30 chars).', h_reserved: 'That name is reserved. Try another.',
      h_current: 'This is your current URL.', h_checking: 'Checking…',
      h_avail: '✓ {h} is available!', h_taken: '✗ {h} is taken. Try another.', h_will_check: 'We’ll check availability when you save.',
      h_taken_short: '✗ Taken. Try another.', h_bad_format: 'Only letters, digits, underscore, hyphen (1–30 chars).',
      h_save_fail: 'Save failed: ', chips_tip: 'Available suggestions:', onb_done: '✓ Done!',
      url_empty: 'Pick a URL name first.', acct_url_empty: 'URL name can’t be empty.',
      saved_redirect: '✓ Saved. The old URL will redirect to the new one.', display_save_fail: 'Display name save failed: ',
      confirm_delete: 'Delete “{name}” from your records?\n(You can still restore it from “Undo” at the bottom-left.)',
      this_show: 'this show', deleted: 'Deleted “{name}”', undo: 'Undo',
      mi_h1: 'Log a musical', mi_open_log: '＋ Log a musical', mi_sheet_record: 'Log a musical',
      mi_sec_records: 'My records', mi_not_recorded: 'Nothing logged yet', mi_add: 'Add', mi_update: 'Update',
      mi_footer_1: 'Search → pick production → auto-fill → year-first date → save & stamp.', mi_footer_2: 'Data lives in your browser (localStorage); artwork is each show’s real cover.',
      mi_loading_lib: 'Loading catalogue…',
      mi_search_ph: 'Type a title in English or Chinese… e.g. phantom / les mis', mi_search_hint: 'Search musicals you’ve seen — English or Chinese; not found? add it manually.',
      mi_no_result: 'No “{v}” in the catalogue', mi_manual_add: '＋ Add manually (type your own title / city)',
      mi_musical: 'Musical', mi_manual_input_lbl: 'Manual entry (shows not in the catalogue)', mi_manual_title: 'Add manually',
      mi_back: '← Back', mi_back_search: '← Back to search', mi_back_prods: '← Back to versions', mi_back_pick_prod: '← Back (pick production)',
      fld_title: 'Title', fld_title_req: 'Title *', fld_city: 'City', fld_venue: 'Theatre', fld_venue_opt: 'Theatre (optional)',
      ph_city: 'e.g. London / Taipei', ph_venue: 'e.g. National Taichung Theater', ph_title: 'Title',
      fld_date_opt: 'Which year・month・day did you see it? (optional)', opt_year: 'Year', opt_month: 'Month', opt_day: 'Day',
      mi_month_n: '{n}', mi_day_n: '{n}',
      fld_time: 'Time (optional)', fld_rating: 'Rating (optional)', fld_seat: 'Seat', ph_seat: 'e.g. Stalls A12 / Circle H23',
      fld_price: 'Price', ph_cur: 'Currency ▾', fld_note: 'Note', ph_note: 'Memories of that night…',
      ds_hint: 'Fill to the day for weekday & monthly stats; just the year is fine — you can add more later.',
      ds_hint2: 'Fill to the day for weekday & monthly stats; just the year works too.',
      mgeo_hint: 'Typing a city or theatre auto-matches the country; if matched, it’s pinned on the map.',
      geo_rematch: 'Changing city/theatre re-matches country coordinates; unmatched still saves as text.',
      geo_no_coord: 'If no coordinates are found, the city/theatre still saves as text (may not show on the map).',
      geo_matched: 'Matched {c}', geo_matched_map: 'Matched {c} · will pin on map',
      disclose_open: '＋ Add details (rating, seat, price, note)', disclose_close: '－ Hide details',
      pick_prod: 'Which production did you see?', prod_versions: '{n} versions', prod_tour: 'Tour',
      prod_cities: '{n} cities · {list}', prod_stations: '{n} stops',
      pick_none: 'None of these — I saw it in another city/year', pick_none_sub: 'Fill it in yourself; we’ll keep the title and artwork',
      pick_city_q: '{label} — which city?', pick_city_none: 'Don’t remember the city', pick_city_none_sub: 'Log this tour for now, add the city later',
      run_playing: 'Playing in {city} {range}', run_recent: 'Recently in {city}',
      venue_city: 'Theatre・City', edit_can_change: 'editable', when_seen: 'When did you see it?', not_required: 'optional',
      star_n: '{n} stars', toast_updated: '✓ Record updated', toast_stamped: '🎭 Stamped! Musical #<b>{n}</b> in your collection',
      date_undated: 'Date TBD', mi_log_ct_n: '{n}',
      recent_added: 'Added this time · {n}', recent_added_sub: 'Made a mistake? Tap ✎ to edit, 🗑 to delete',
      recent_empty: 'Search musicals you’ve seen — English or Chinese; not found? add it manually.', recent_empty_sub: 'What you add grows onto your poster wall and passport instantly.',
      mi_edit_record: 'Edit record', mi_added: 'Added',
      added_one: '🎭 Added “{name}”!', added_n: '🎭 Added <b>{n}</b>!',
      batch_hint: 'Want to log the date or rating? Tap a show below to fill it in — optional; you can always tap ✎ on the poster card later.',
      date_later: 'Add date later', seat_label: 'Seat <b>{v}</b>', price_label: 'Price <b>{v}</b>', edit_btn: '✎ Edit',
      add_more: '＋ Add another', batch_done: 'Done, back to my collection →',
      fld_poster: 'Poster URL (optional)', ph_poster: 'Paste an image URL to override the default; clear to restore', poster_prev: 'Preview',
      fld_link: 'Link / ticket URL (optional)', ph_link: 'Paste the ticket or programme link (optional)',
      mi_intro: 'Most people add shows they saw years ago, so the date isn’t preset to today — pick a show and we use its run dates to help you recall the year; theatre, city and artwork auto-fill, so you barely type.',
      mi_hint: 'Try: type “phantom”, “les mis”, or a Chinese title. Data comes from MusicalMap’s real catalogue.',
      mi_stamp_here: 'stamp<br>here', mi_empty_passport: 'Your passport is still blank.<br><b>Tap “＋ Log a musical” above</b> to add your first stamp.',
      how_title: 'How it works — MusicalMap',
      how_meta: 'How MusicalMap works: one live map of musicals playing worldwide, and a theatre passport for every show you’ve seen.',
      how_nav_start: 'My Musicals', how_eyebrow: 'How it works',
      how_hero: 'One map for<br>every musical playing <em>right now</em>.',
      how_lede: 'Explore what’s on around the world without signing in — Broadway, the West End, tours everywhere. Sign in, and every show you’ve seen becomes a theatre passport you can share.',
      how_cta_map: 'Explore the map', how_cta_me: 'Build your passport',
      how_p1_h: 'Explore — no sign-up', how_p1_lede: 'Open the map and see what’s playing around the world right now. Found one you like? Go straight to tickets.',
      how_a1_n: 'On the map', how_a1_h: 'Every poster on the map is a show playing now', how_a1_p: 'Markers are the shows’ own posters; nearby ones gather into a numbered circle — that’s how many are playing around there. Tap a poster for its dates, theatre and ticket links.',
      how_a2_n: 'One tap to tickets', how_a2_h: 'See one you like? Go straight there', how_a2_p: 'Every show comes with a ticket link, and most have their official site too. We don’t sell tickets — we just point you to the right place.',
      how_bridge: 'Don’t let the ones you’ve seen live only in memory.',
      how_p2_h: 'Keep every show you’ve seen', how_p2_lede: 'Once you sign in, your shows grow into a poster wall, a stamped passport and your own viewing stats. All automatic.',
      how_b1_n: 'Add a show', how_b1_h: 'Search the title, the rest fills itself in', how_b1_p: 'Search in English or Chinese; theatre, city and poster fill in automatically. Add the date, rating, seat and notes — just the year is fine. Every show you log adds a stamp to your passport.',
      how_b2_n: 'Your viewing stats', how_b2_h: 'Watch enough, and a shape emerges', how_b2_p: 'Most-seen shows, cities and countries visited, how your viewing spreads across years and months — no counting needed, just who you are as a theatregoer.',
      how_b3_n: 'Share it', how_b3_h: 'Your own page, one URL to share', how_b3_p: 'Pick a URL name and you get a public page to send to friends. You decide whether price and seat are shown; your notes stay yours alone.',
      how_b4_n: 'Signing in is simple', how_b4_h: 'Sign in with Google, synced everywhere', how_b4_p: 'We only read your name and email — we never post anything on your behalf. Your collection lives in your account, on every phone and laptop.',
      how_final_h: 'Start anywhere', how_final_p: 'Browse the map for inspiration, or just log the first show you’ve seen.', how_final_cta: 'Build your passport', how_final_cta2: 'Explore the map first',
      how_footer: 'MusicalMap — a live world map of musicals, and your theatre passport.', how_footer_link: 'Back to the map',
    },
  };

  // ---- 語言解析(?hl 進網址是 SEO 需求;navigator 只服務沒帶參數的真人) ----
  var q = null;
  try { q = new URLSearchParams(location.search).get('hl'); } catch (e) {}
  var hl = (q === 'en' || q === 'zh-hant' || q === 'zh-hans') ? q : null;
  if (!hl && window.MM_HL && STR[window.MM_HL === 'zh-hans' ? 'zh-hant' : window.MM_HL]) hl = window.MM_HL; // Worker 注入
  // 登入頁(me.html)設 MM_USE_LANG_PREF → 讀主站共用的 mm_lang 偏好(en/zh)。公開頁 u.html 不設(語言只認 ?hl=,SEO 需求)。
  if (!hl && window.MM_USE_LANG_PREF) {
    try {
      var mv = localStorage.getItem('mm_variant');   // 主站存 en/zh-hans/zh-hant(精確含簡繁),優先
      if (mv === 'en' || mv === 'zh-hans' || mv === 'zh-hant') hl = mv;
      else { var lp = localStorage.getItem('mm_lang'); if (lp === 'en') hl = 'en'; else if (lp === 'zh') hl = 'zh-hant'; }
    } catch (e) {}
  }
  if (!hl) {
    var nl = (navigator.language || '').toLowerCase();
    if (nl.indexOf('zh') === 0) hl = (nl.indexOf('cn') > -1 || nl.indexOf('hans') > -1 || nl.indexOf('sg') > -1) ? 'zh-hans' : 'zh-hant';
    else if (nl) hl = 'en';
    else hl = 'zh-hant';
  }
  // zh-hans:用 OpenCC(tw→cn)把繁中字典 runtime 轉簡體(沿用主站 i18n.js 機制);OpenCC 未載入則降級繁中。
  var _conv = null;
  if (hl === 'zh-hans') {
    try { _conv = window.OpenCC && window.OpenCC.Converter({ from: 'tw', to: 'cn' }); } catch (e) {}
    if (_conv && !STR['zh-hans']) { var o = {}; for (var k in STR['zh-hant']) o[k] = _conv(STR['zh-hant'][k]); STR['zh-hans'] = o; }
  }
  var D = STR[hl] || STR['zh-hant'];
  // MM_S:把「資料層繁中文字」(劇院/城市/國家名,原始資料)在 zh-hans 也轉簡;其他語言 identity。
  // u-view.js / me.html 的 countryZh/cityName/venueZh 用它,讓簡體頁不殘留繁體地名。
  window.MM_S = _conv ? function (t) { try { return _conv(String(t == null ? '' : t)); } catch (e) { return t; } } : function (t) { return t; };

  window.MM_STR = STR;
  window.MM_HL = hl;
  window.MM_T = function (k) {
    if (D[k] != null) return D[k];
    if (STR['zh-hant'][k] != null) return STR['zh-hant'][k];
    return k;
  };

  // ---- 套用到靜態 DOM:data-i18n(textContent)/-title/-aria;<html lang>;語言切換 pills ----
  function apply() {
    document.documentElement.lang = hl === 'en' ? 'en' : (hl === 'zh-hans' ? 'zh-Hans' : 'zh-Hant');
    if (window.MM_USE_LANG_PREF) { try { localStorage.setItem('mm_lang', hl === 'en' ? 'en' : 'zh'); localStorage.setItem('mm_variant', hl); } catch (e) {} } // 記住偏好(mm_variant 含簡繁,與主站共用)
    document.querySelectorAll('[data-i18n]').forEach(function (el) { el.textContent = window.MM_T(el.getAttribute('data-i18n')); });
    document.querySelectorAll('[data-i18n-html]').forEach(function (el) { el.innerHTML = window.MM_T(el.getAttribute('data-i18n-html')); });  // 含 <br>/<b> 的字串(字典值為信任的 UI 文案,非使用者輸入)
    document.querySelectorAll('[data-i18n-title]').forEach(function (el) { el.title = window.MM_T(el.getAttribute('data-i18n-title')); });
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) { el.setAttribute('aria-label', window.MM_T(el.getAttribute('data-i18n-aria'))); });
    document.querySelectorAll('[data-i18n-content]').forEach(function (el) { el.setAttribute('content', window.MM_T(el.getAttribute('data-i18n-content'))); });  // <meta> description/og
    // 語言切換:改寫 ?hl= 並保留其他參數(如 ?u=)——連結而非按鈕,爬蟲也能發現語言變體。
    // 繁也要「明寫 ?hl=zh-hant」:若刪參數,簡體/英文瀏覽器會被 navigator 重新偵測回原語言,永遠切不回繁
    // (無參數 URL 仍是 zh-hant canonical,由各頁 hreflang/canonical 標記,同 theatres.html ?lang= 模式)。
    document.querySelectorAll('[data-hl-link]').forEach(function (a) {
      var t = a.getAttribute('data-hl-link');
      var u = new URL(location.href);
      u.searchParams.set('hl', t);
      a.href = u.pathname + (u.search || '');
      if (t === hl) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current');
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
  window.MM_APPLY_I18N = apply;
})();
