/* mm-persona-radar.js — 「你是什麼樣的劇迷」五邊形戰力圖 + 解釋清單(me/u 共用)
   輸入 radar.items = [{nm,ds,ev,v}×5]。渲染:金屬外框雷達圖(大標籤+分數+閃爍+光澤)+ 每軸解釋清單。
   依主題自動配色:亮色(cream/gallery)=香檳金箔;暗色(midnight)=靛藍月光。切主題會重繪。 */
(function(){
  var NS="http://www.w3.org/2000/svg";
  function mk(t,a){var n=document.createElementNS(NS,t);for(var k in a)if(a[k]!=null)n.setAttribute(k,a[k]);return n;}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var STYLE={
    light:{
      svgBg:"radial-gradient(circle at 50% 34%,#fbf4dd,#f0e3bf 60%,#e7d3a0)",
      fill:[[0,"#e7b53c",.9],[55,"#d59a2c",.62],[100,"#b57e20",.42]],
      stroke:"#a9781f",sw:2.6,grid:"#d3bf8e",gridO:"#a9781f",band:"rgba(180,140,40,.09)",
      label:"#5a4415",val:"#8a6a28",glowStd:2.2,sparkle:"#fff2c0",dot:"#7a5c18",
      frame:"conic-gradient(from 140deg,#e9c977,#fff6da 12%,#c99a3a 30%,#f6e4a8 55%,#b9812a 74%,#f3dc98 90%,#e9c977)",
      barTrack:"#e3d6b8", cols:["#c0392b","#b8860b","#2e7d5b","#7a4fb0","#c07a1c"]
    },
    dark:{
      svgBg:"radial-gradient(circle at 50% 26%,#26356e,#141f42 62%,#0b1230)",
      fill:[[0,"#8fa8ff",.85],[55,"#5f79df",.55],[100,"#2c3f86",.36]],
      stroke:"#e3ebff",sw:2.4,grid:"#2e3d70",gridO:"#54689f",band:"rgba(120,150,255,.08)",
      label:"#c6d2f5",val:"#c3d0f5",dark:1,glowStd:3.4,sparkle:"#ffffff",dot:"#eef2ff",
      frame:"conic-gradient(from 140deg,#3d5296,#c3d0f5 12%,#26386f 30%,#8fa4dd 55%,#1a2c5c 74%,#aebde8 90%,#3d5296)",
      barTrack:"#26305a", cols:["#ff6f61","#ffcf5c","#4fd6a6","#a98bff","#ffb25e"]
    }
  };
  var _seq=0;
  function buildSVG(items,st){
    var N=items.length,S=300,cx=S/2,cy=S/2,R=S/2-46;
    function ang(i){return(-90+i*360/N)*Math.PI/180;}
    function pt(i,f){var a=ang(i);return[cx+Math.cos(a)*R*f,cy+Math.sin(a)*R*f];}
    function ring(f){var p=[];for(var i=0;i<N;i++){var q=pt(i,f);p.push(q[0].toFixed(1)+","+q[1].toFixed(1));}return p.join(" ");}
    var svg=mk("svg",{viewBox:"0 0 "+S+" "+S,width:"100%",style:"display:block;height:auto;border-radius:13px;background:"+st.svgBg+";font-family:'Noto Sans TC',sans-serif"});
    var gid="rg"+(++_seq),glid="gl"+_seq;
    var defs=mk("defs",{});
    var stops=st.fill.map(function(s){return '<stop offset="'+s[0]+'%" stop-color="'+s[1]+'" stop-opacity="'+s[2]+'"/>';}).join("");
    defs.innerHTML='<radialGradient id="'+gid+'" cx="50%" cy="42%" r="62%">'+stops+'</radialGradient>'
      +'<filter id="'+glid+'" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="'+st.glowStd+'" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
    svg.appendChild(defs);
    for(var r=1;r<=4;r++)svg.appendChild(mk("polygon",{points:ring(r/4),fill:(r%2)?st.band:"none",stroke:r===4?st.gridO:st.grid,"stroke-opacity":r===4?.6:.34,"stroke-width":r===4?1.5:1,"stroke-linejoin":"round"}));
    for(var i=0;i<N;i++){var o=pt(i,1);svg.appendChild(mk("line",{x1:cx,y1:cy,x2:o[0].toFixed(1),y2:o[1].toFixed(1),stroke:st.grid,"stroke-opacity":.4,"stroke-width":1}));}
    // 頂點半徑最低邊界:新手數值很小(如 5)也畫到 ~12%,五邊形不塌成中心一坨;標籤分數與清單仍顯示真實值(2026-07-16)
    var FLOOR=0.12; function posf(v){return Math.max(FLOOR, Math.max(0,Math.min(100,v))/100);}
    var dp=[];for(var i=0;i<N;i++){var q=pt(i,posf(items[i].v));dp.push(q[0].toFixed(1)+","+q[1].toFixed(1));}
    svg.appendChild(mk("polygon",{points:dp.join(" "),fill:"url(#"+gid+")",stroke:st.stroke,"stroke-width":st.sw,"stroke-linejoin":"round",filter:"url(#"+glid+")"}));
    for(var i=0;i<N;i++){var a=ang(i),lx=cx+Math.cos(a)*(R+30),ly=cy+Math.sin(a)*(R+30),cv=Math.cos(a),sv=Math.sin(a);
      var anc=Math.abs(cv)<.3?"middle":(cv>0?"start":"end"),dy=sv<-.6?-4:(sv>.6?14:3);
      var t=mk("text",{x:lx.toFixed(1),y:(ly+dy).toFixed(1),"text-anchor":anc,fill:st.label,"font-size":15,"font-weight":"800"});t.textContent=items[i].nm;svg.appendChild(t);
      var s2=mk("text",{x:lx.toFixed(1),y:(ly+dy+16).toFixed(1),"text-anchor":anc,fill:st.val,"font-size":13,"font-weight":"900"});s2.textContent=Math.round(items[i].v);svg.appendChild(s2);}
    for(var i=0;i<N;i++){var q=pt(i,posf(items[i].v));svg.appendChild(mk("circle",{cx:q[0].toFixed(1),cy:q[1].toFixed(1),r:3.4,fill:st.dot,stroke:st.dark?"#0006":"#fff","stroke-width":1.5}));}
    var mx=0;for(var i=1;i<N;i++)if(items[i].v>items[mx].v)mx=i;var mp=pt(mx,posf(items[mx].v));
    var sp=mk("text",{x:mp[0].toFixed(1),y:(mp[1]-8).toFixed(1),"text-anchor":"middle","font-size":16,fill:st.sparkle});sp.textContent="✦";svg.appendChild(sp);
    return svg;
  }
  function isLight(){var th=document.documentElement.getAttribute('data-theme');return th==='cream'||th==='gallery';}
  window.mmRenderPersona=function(el,radar){
    el=(typeof el==='string')?document.querySelector(el):el; if(!el||!radar||!radar.items)return;
    var st=isLight()?STYLE.light:STYLE.dark, items=radar.items;
    el.className='pradar';
    el.innerHTML='<div class="radar-frame" style="background:'+st.frame+'"><div class="rf-in" id="rf-svg"></div></div>'
      +'<div class="plegend">'+items.map(function(it,i){
        var c=st.cols[i], v=Math.max(0,Math.min(100,Math.round(it.v)));
        return '<div class="lg"><div class="ix" style="background:'+c+'">'+(i+1)+'</div>'
          +'<div class="lg-t"><div class="nm">'+esc(it.nm)+'</div><div class="ds" style="color:'+(st.dark?'#9aa6c6':'#6b5836')+'">'+esc(it.ds)+' · '+esc(it.ev)+'</div></div>'
          +'<div class="sc"><span class="val" style="color:'+st.val+'">'+v+'</span>'
          +'<div class="bar" style="background:'+st.barTrack+'"><i style="width:'+v+'%;background:'+c+'"></i></div></div></div>';
      }).join('')+'</div>';
    el.querySelector('#rf-svg').appendChild(buildSVG(items,st));
    // 標籤在 300×300 外圈,用 getBBox 撐開 viewBox 避免左右字被切
    var svg=el.querySelector('svg');
    try{var bb=svg.getBBox(),pad=6;svg.setAttribute('viewBox',(bb.x-pad).toFixed(1)+' '+(bb.y-pad).toFixed(1)+' '+(bb.width+2*pad).toFixed(1)+' '+(bb.height+2*pad).toFixed(1));}catch(e){}
  };
})();
