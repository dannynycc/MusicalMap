/* me-catalog.js — 輸入端劇庫資料層（取代舊 catalog.js）
   非同步 fetch 正式版資料：
     data/venues_catalog.json  → window.MM_VC   (titles/productions/posters/venues/cities/currencies)
     data/shows.json           → window.MM_SHOWS (當期演出，含 venue/city/country/lat/lng/檔期)
   只負責「取得原始資料」；CATALOG/INDEX 的組裝在 me-input.html（那裡有 curOf/norm 等 helper）。
   window.MM_DATA_READY 是一個 Promise，資料就緒後 resolve(true)，失敗 resolve(false)。 */
(function(){
  window.MM_VC = null;
  window.MM_SHOWS = [];
  window.MM_DATA_READY = (async function(){
    try{
      const [vc, sj] = await Promise.all([
        fetch('data/venues_catalog.json').then(r=>{ if(!r.ok) throw new Error('venues_catalog '+r.status); return r.json(); }),
        fetch('data/shows.json').then(r=>{ if(!r.ok) throw new Error('shows '+r.status); return r.json(); })
      ]);
      window.MM_VC = vc;
      window.MM_SHOWS = (sj && sj.shows) ? sj.shows : [];
      return true;
    }catch(e){
      console.error('[me-catalog] 劇庫載入失敗', e);
      window.MM_VC = { titles:[], productions:{}, posters:{}, venues:[], cities:[], currencies:[] };
      window.MM_SHOWS = [];
      return false;
    }
  })();
})();
