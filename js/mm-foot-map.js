/* mm-foot-map.js — 足跡地圖 v2:主站同款 Leaflet + 扇形疊卡(場館級 pin)。
   me.html 與 u.html 共用(取代各自的自繪 canvas 點陣地圖,兩處必同步改的舊坑就此收斂)。

   設計(2026-07-17 使用者定案,經 7 版提案迭代):
   - 每一「場」= 一張首頁同款海報圖卡;同一間劇院的場次攤成一手牌(扇形疊卡),
     張數本身就是數量 —— 不放任何數字圓圈。
   - pin 在「實際看戲的劇院」座標(記錄在輸入時從 venues_catalog 選的場館級 lat/lng);
     拉遠時 markercluster 把附近的牌疊成更大一手,點疊牌自動 zoom 進去攤開。
   - 未來場次(即將)= 虛線降飽和卡+「即將」小標;點牌開該劇院字卡(海報縮圖+劇名+日期),
     字卡底部「只看這座城市」沿用 filterToCity 行為。
   - 底圖=主站 Mapbox streets-v12(token 綁 themusicalmap.com,涵蓋 my. 子網域,已驗證)。
   無座標的記錄不放 pin(城市清單/統計照算,絕不消失)。 */
(function(){
'use strict';
const FALLBACK={
  map_card_shows:'{n} 場', map_card_up:'即將', map_card_up_n:'即將 · {n} 場',
  map_card_only_city:'只看這座城市', map_aria:'音樂劇足跡地圖 / Musicals visited map',
};
function mount(opts){
  const {el,records,T,TN,esc,cityName,countryZh,venueZh,isPast,onCityFilter}=opts;
  if(!el||!window.L)return null;
  const t=k=>{const v=T?T(k):null;return (v&&v!==k)?v:FALLBACK[k]||k;};
  const tn=(k,vars)=>{let s=t(k);for(const n in(vars||{}))s=s.replace('{'+n+'}',vars[n]);return s;};

  // ---- 場館分組(venue+座標;座標四捨五入避免浮點分裂) ----
  const groups=new Map();
  records.forEach(s=>{
    if(!s.venue||s.lat==null||s.lng==null)return;
    const key=venueZh(s.venue)+'|'+(+s.lat).toFixed(4)+','+(+s.lng).toFixed(4);
    let g=groups.get(key);
    if(!g){g={venue:s.venue,city:s.city,country:s.country,lat:+s.lat,lng:+s.lng,shows:[]};groups.set(key,g);}
    g.shows.push(s);
  });
  if(!groups.size)return null;

  const token=(window.MM_CONFIG&&window.MM_CONFIG.MAPBOX_TOKEN)||'';
  // minZoom:1=圖磚下限。512px 圖磚+zoomOffset:-1 → 圖磚 z=地圖 z-1;手機窄容器 fitBounds
  // 會把地圖壓到 z0 → 要抓 z=-1 圖磚(不存在)→ 整片空白(2026-07-17 手機回報)。z1 起跳圖磚 z0 存在。
  const map=L.map(el,{worldCopyJump:true,zoomControl:true,attributionControl:true,minZoom:1});
  // 窄容器(手機)卡片縮小,免得一手牌蓋滿整張地圖
  const SC=el.clientWidth<520?0.72:1;
  map.getContainer().setAttribute('aria-label',t('map_aria'));
  L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/512/{z}/{x}/{y}@2x?access_token='+token,{
    attribution:'&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    tileSize:512,zoomOffset:-1,maxZoom:19}).addTo(map);

  // ---- 扇形疊卡 icon:cards=[{poster,fut}],舊→新(最新一張疊最上) ----
  function fanIcon(cards){
    const n=cards.length;
    const spread=n>1?Math.min(15,150/(n-1))*SC:0;
    const rot=n>1?Math.min(7,44/(n-1)):0;
    const cw=Math.round(52*SC),ch=Math.round(72*SC);
    const width=(cw+12)+(n-1)*spread,height=ch+20,mid=(n-1)/2;
    const html=cards.map((c,i)=>{
      const dx=(i-mid)*spread,dg=(i-mid)*rot;
      const bg=c.poster?'background-image:url(\''+c.poster.replace(/'/g,'%27')+'\');':'';
      return '<span class="fcard'+(c.fut?' fup':'')+'" style="width:'+cw+'px;height:'+ch+'px;transform:translateX(calc(-50% + '+dx+'px)) rotate('+dg+'deg);z-index:'+i+';'+bg+'">'+(c.poster?'':'♪')+'</span>';
    }).join('');
    return L.divIcon({className:'mm-fan-icon',
      html:'<div class="fan">'+html+'</div>',
      iconSize:[width,height],iconAnchor:[width/2,height-6],popupAnchor:[0,-height+10]});
  }
  const cardsOf=shows=>[...shows].sort((a,b)=>String(a.date).localeCompare(String(b.date)))
      .map(s=>({poster:s.poster||null,fut:!isPast(s.date),date:s.date}));

  const cluster=L.markerClusterGroup({maxClusterRadius:96,spiderfyOnMaxZoom:true,showCoverageOnHover:false,
    iconCreateFunction:c=>{
      let all=[];c.getAllChildMarkers().forEach(m=>{all=all.concat(m.options.mmCards||[]);});
      all.sort((a,b)=>String(a.date).localeCompare(String(b.date)));
      return fanIcon(all);}});
  map.addLayer(cluster);

  // ---- 劇院字卡(首頁圖卡語言;顏色走主題變數,深淺主題自適應) ----
  function cardHTML(g){
    const shows=[...g.shows].sort((a,b)=>String(b.date).localeCompare(String(a.date)));
    const past=shows.filter(s=>isPast(s.date)).length,fut=shows.length-past;
    const hp=(shows.find(s=>s.poster)||{}).poster||'';
    const rows=shows.map(s=>{
      const zh=s.zh||'',en=s.title||'';
      const name=zh?esc(zh)+'<small>'+esc(en)+'</small>':esc(en);
      const d=String(s.date||'').replace(/-/g,'/');
      return '<li><span class="p" style="'+(s.poster?'background-image:url(\''+esc(s.poster)+'\')':'')+'">'+(s.poster?'':'♪')+'</span>'
        +'<span class="m"><span class="t">'+name+'</span>'
        +'<span class="v">'+esc(venueZh(g.venue))+' · '+esc(cityName(g.city))+'</span></span>'
        +'<span class="d">'+(isPast(s.date)?esc(d):'<b class="up">'+t('map_card_up')+'</b> '+esc(d))+'</span></li>';
    }).join('');
    const chip=past?tn('map_card_shows',{n:past})+(fut?' · '+tn('map_card_up_n',{n:fut}):''):tn('map_card_up_n',{n:fut});
    return '<div class="footcard">'
      +'<div class="hd"><span class="bg" style="background-image:url(\''+esc(hp)+'\')"></span>'
      +'<span class="hp" style="background-image:url(\''+esc(hp)+'\')">'+(hp?'':'♪')+'</span>'
      +'<span class="hm"><span class="cc">'+esc(cityName(g.city))+(g.country?' · '+esc(countryZh(g.country)):'')+'</span>'
      +'<span class="ct">'+esc(venueZh(g.venue))+'</span>'
      +'<span class="chip">'+chip+'</span></span></div>'
      +'<ul>'+rows+'</ul>'
      +(onCityFilter?'<button class="ftbtn" data-city="'+esc(g.city)+'">'+t('map_card_only_city')+'</button>':'')
      +'</div>';
  }

  const bounds=[];
  groups.forEach(g=>{
    const cards=cardsOf(g.shows);
    const m=L.marker([g.lat,g.lng],{icon:fanIcon(cards),riseOnHover:true,
      title:venueZh(g.venue),mmCards:cards,keyboard:true,alt:venueZh(g.venue)});
    m.bindPopup(()=>cardHTML(g),{className:'mm-footpop',maxWidth:352});
    cluster.addLayer(m);bounds.push([g.lat,g.lng]);
  });
  map.on('popupopen',e=>{
    const b=e.popup.getElement().querySelector('.ftbtn');
    if(b)b.onclick=()=>{map.closePopup();onCityFilter&&onCityFilter(b.dataset.city);};
  });
  const fit=()=>map.fitBounds(bounds,{padding:[46,46],maxZoom:11});
  fit();
  // 掛載常發生在 async 資料載完之後:容器當下可能還是 0 高(字體/版面未定),
  // 之後長高若不 invalidateSize,圖磚範圍=0 → 一片空白+標記貼頂(2026-07-17 手機實測)。
  // ResizeObserver 盯容器尺寸;首度從 0 → 有效尺寸時重新 fitBounds 一次。
  let fitted=el.clientHeight>0;
  const ro=new ResizeObserver(()=>{map.invalidateSize();
    if(!fitted&&el.clientHeight>0){fitted=true;fit();}});
  ro.observe(el);
  requestAnimationFrame(()=>{map.invalidateSize();if(!fitted&&el.clientHeight>0){fitted=true;fit();}});
  return map;
}
window.MMFootMap={mount};
})();
