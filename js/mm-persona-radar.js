/* mm-persona-radar.js — 「你是什麼樣的劇迷」五邊形戰力圖(me/u 共用)
   5 軸:探索者·世界劇種通·環球玩家·忠誠鐵粉·資深老手(值 0–100,由 data.js personality().radar 供給)。
   依主題自動上色:亮色(cream/gallery)=香檳金箔;暗色(midnight)=靛藍月光。切主題會重繪。 */
(function(){
  var STYLE={
    // 3 香檳金箔(亮)
    light:{bg:"linear-gradient(160deg,#faf6ec,#f1e7cf)",fill:[[0,"#c9a24a",.55],[100,"#e8d29a",.28]],stroke:"#a07a34",sw:2,grid:"#d8c79c",gridO:"#a07a34",label:"#6b5320",dot:"#8a6a28"},
    // 10 靛藍月光(暗)
    dark:{bg:"radial-gradient(circle at 50% 25%,#1a2c5c,#101c3d 65%,#080f24)",fill:[[0,"#6f8cff",.55],[100,"#26386f",.28]],stroke:"#dfe7ff",sw:1.8,grid:"#28386b",gridO:"#3d5296",label:"#c3d0f5",dark:1,sparkle:"#eef2ff",dot:"#eef2ff"}
  };
  var _seq=0;   // 遞增序號:每次渲染給漸層/濾鏡唯一 id,避免同文件多張圖 url(#id) 撞到第一個定義
  function draw(el,axes,values,st){
    var N=axes.length,S=300,cx=S/2,cy=S/2,R=S/2-40,NS="http://www.w3.org/2000/svg";
    function mk(t,a){var n=document.createElementNS(NS,t);for(var k in a)n.setAttribute(k,a[k]);return n;}
    function ang(i){return(-90+i*360/N)*Math.PI/180;}
    function pt(i,f){var a=ang(i);return[cx+Math.cos(a)*R*f,cy+Math.sin(a)*R*f];}
    function ring(f){var p=[];for(var i=0;i<N;i++){var q=pt(i,f);p.push(q[0].toFixed(1)+","+q[1].toFixed(1));}return p.join(" ");}
    el.textContent="";
    var svg=mk("svg",{viewBox:"0 0 "+S+" "+S,width:"100%",style:"display:block;max-width:300px;margin:0 auto;height:auto;background:"+st.bg+";border-radius:14px;font-family:'Noto Sans TC',sans-serif"});
    var gid="rgp"+(++_seq),glid="glp"+_seq;
    var defs=mk("defs",{});
    var stops=st.fill.map(function(s){return '<stop offset="'+s[0]+'%" stop-color="'+s[1]+'" stop-opacity="'+s[2]+'"/>';}).join("");
    defs.innerHTML='<linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1">'+stops+'</linearGradient>'
      +'<filter id="'+glid+'" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>';
    svg.appendChild(defs);
    for(var r=1;r<=4;r++)svg.appendChild(mk("polygon",{points:ring(r/4),fill:(r%2)?(st.dark?'rgba(255,255,255,.05)':'rgba(0,0,0,.03)'):"none",stroke:r===4?st.gridO:st.grid,"stroke-opacity":r===4?.55:.32,"stroke-width":r===4?1.4:1,"stroke-linejoin":"round"}));
    for(var i=0;i<N;i++){var o=pt(i,1);svg.appendChild(mk("line",{x1:cx,y1:cy,x2:o[0].toFixed(1),y2:o[1].toFixed(1),stroke:st.grid,"stroke-opacity":.35,"stroke-width":1}));}
    for(var i=0;i<N;i++){var a=ang(i),lx=cx+Math.cos(a)*(R+26),ly=cy+Math.sin(a)*(R+26),cv=Math.cos(a),sv=Math.sin(a);
      var anc=Math.abs(cv)<.3?"middle":(cv>0?"start":"end"),dy=sv<-.6?-2:(sv>.6?11:5);
      var t=mk("text",{x:lx.toFixed(1),y:(ly+dy).toFixed(1),"text-anchor":anc,fill:st.label,"font-size":12,"font-weight":"700"});t.textContent=axes[i];svg.appendChild(t);}
    var dp=[];for(var i=0;i<N;i++){var v=Math.max(0,Math.min(100,values[i]))/100,q=pt(i,v);dp.push(q[0].toFixed(1)+","+q[1].toFixed(1));}
    svg.appendChild(mk("polygon",{points:dp.join(" "),fill:"url(#"+gid+")",stroke:st.stroke,"stroke-width":st.sw,"stroke-linejoin":"round",filter:st.dark?"url(#"+glid+")":null}));
    for(var i=0;i<N;i++){var v=Math.max(0,Math.min(100,values[i]))/100,q=pt(i,v);svg.appendChild(mk("circle",{cx:q[0].toFixed(1),cy:q[1].toFixed(1),r:2.8,fill:st.dot||st.stroke,stroke:st.dark?'#0008':'#faf6ec',"stroke-width":1.4}));}
    if(st.sparkle){var mx=0;for(var i=1;i<N;i++)if(values[i]>values[mx])mx=i;var mp=pt(mx,Math.max(0,Math.min(100,values[mx]))/100);
      var sp=mk("text",{x:mp[0].toFixed(1),y:(mp[1]-6).toFixed(1),"text-anchor":"middle","font-size":13,fill:st.sparkle});sp.textContent="✦";svg.appendChild(sp);}
    el.appendChild(svg);
    try{var bb=svg.getBBox(),pad=6;svg.setAttribute("viewBox",(bb.x-pad).toFixed(1)+" "+(bb.y-pad).toFixed(1)+" "+(bb.width+2*pad).toFixed(1)+" "+(bb.height+2*pad).toFixed(1));}catch(e){}
  }
  // 依目前主題挑配色:cream/gallery=亮;其餘(midnight,無 data-theme)=暗
  function isLight(){var th=document.documentElement.getAttribute('data-theme');return th==='cream'||th==='gallery';}
  window.mmRenderPersona=function(el,axes,values){
    el=(typeof el==='string')?document.querySelector(el):el; if(!el)return;
    draw(el,axes,values,isLight()?STYLE.light:STYLE.dark);
  };
})();
