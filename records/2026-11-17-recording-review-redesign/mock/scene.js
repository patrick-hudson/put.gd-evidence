// ---------- the recorded screen (a fake browser session) ----------
function scene(c,w,h,t,masks){
 const s=w/1452;c.save();c.scale(s,s);w=1452;h=816;
 c.fillStyle='#1d2430';c.fillRect(0,0,w,h);
 // wallpaper
 const g=c.createLinearGradient(0,0,w,h);g.addColorStop(0,'#26314a');g.addColorStop(1,'#141b28');c.fillStyle=g;c.fillRect(0,0,w,h);
 // panel
 c.fillStyle='#2b313d';c.fillRect(0,h-40,w,40);for(let i=0;i<5;i++){c.fillStyle=i==1?'#5b8def':'#6b7383';c.beginPath();c.roundRect(20+i*40,h-32,24,24,5);c.fill()}c.fillStyle='#c9ced8';c.font='15px Plex';c.fillText('14:02',w-70,h-15);
 if(t<2.0){ // idle desktop, terminal minimised
  c.fillStyle='rgba(255,255,255,.08)';for(let i=0;i<4;i++){c.fillRect(30,40+i*110,72,72)}
  c.restore();return}
 // browser window
 const bx=70,by=36,bw=w-140,bh=h-110;
 c.fillStyle='#f4f4f2';rr(c,bx,by,bw,bh,12);c.fill();
 c.fillStyle='#e3e3df';rr(c,bx,by,bw,58,12);c.fill();c.fillRect(bx,by+40,bw,18);
 ['#ff6b5e','#febd2f','#29c840'].forEach((col,i)=>{c.fillStyle=col;c.beginPath();c.arc(bx+24+i*22,by+22,7,0,7);c.fill()});
 c.fillStyle='#fff';rr(c,bx+110,by+10,bw-220,26,13);c.fill();
 c.fillStyle='#55554f';c.font='15px Plex';c.fillText(t<19.5?'console.example.dev/login':'console.example.dev/deploys/4182',bx+132,by+28);
 const cx=bx+bw/2;
 if(t<12.6){ // login
  const step=Math.min(1,(t-2.0)/5.5);
  c.fillStyle='#fff';rr(c,cx-230,by+120,460,440,16);c.fill();c.strokeStyle='#e2e2dd';c.lineWidth=2;c.stroke();
  c.fillStyle='#1c1c1a';c.font='600 30px Plex';c.textAlign='center';c.fillText('Sign in to Console',cx,by+190);
  c.font='16px Plex';c.fillStyle='#7a7a74';c.fillText('Production environment',cx,by+220);c.textAlign='left';
  field(c,cx-190,by+262,'Username','deploy-bot@acme.io'.slice(0,Math.round(18*step)),t<8.2);
  const pw='hunter2hunter2';const pstep=t<8.2?0:Math.min(1,(t-8.2)/1.6);
  field(c,cx-190,by+352,'Password',pw.slice(0,Math.round(pw.length*pstep)),t>=8.2,true);
  c.fillStyle=t>11.4?'#2d5bd8':'#3b6cf0';rr(c,cx-190,by+460,380,52,10);c.fill();
  c.fillStyle='#fff';c.font='600 18px Plex';c.textAlign='center';c.fillText('Sign in',cx,by+493);c.textAlign='left';
  if(masks&&t>=MASK[0]&&t<MASK[1]){ // the cover, as exported
   c.fillStyle='#000';c.fillRect(cx-196,by+360,392,56);
  }
  cursor(c,t>11?cx+40:cx+150,t>11?by+490:by+420);
 } else if(t<19.5){ // deploying
  const p=(t-12.6)/6.9;
  c.fillStyle='#1c1c1a';c.font='600 28px Plex';c.fillText('Deploying build 4182…',bx+90,by+150);
  c.fillStyle='#e6e6e1';rr(c,bx+90,by+190,bw-180,14,7);c.fill();c.fillStyle='#3b6cf0';rr(c,bx+90,by+190,(bw-180)*(.08+.5*p),14,7);c.fill();
  c.font='15px PlexMono';c.fillStyle='#8a8a83';
  for(let i=0;i<Math.floor(3+p*9);i++)c.fillText(['pull image  ✓','migrate db  ✓','warm cache  …','health check …'][i%4]+'  '+(12+i*3)+'s',bx+90,by+250+i*28);
  spinner(c,bx+bw-130,by+140,t);
 } else { // done
  c.fillStyle='#e9f5ee';rr(c,bx+90,by+110,bw-180,96,12);c.fill();
  c.fillStyle='#2f9e5d';c.beginPath();c.arc(bx+140,by+158,22,0,7);c.fill();c.strokeStyle='#fff';c.lineWidth=4;c.beginPath();c.moveTo(bx+129,by+158);c.lineTo(bx+137,by+167);c.lineTo(bx+152,by+149);c.stroke();
  c.fillStyle='#14361f';c.font='600 26px Plex';c.fillText('Build 4182 is live',bx+180,by+152);c.font='16px Plex';c.fillStyle='#3f6b4f';c.fillText('3 regions · 0 errors · 41 s',bx+180,by+180);
  for(let i=0;i<5;i++){c.fillStyle=i%2?'#f4f4f2':'#ececE8';c.fillRect(bx+90,by+240+i*52,bw-180,52);c.fillStyle='#55554f';c.font='16px Plex';c.fillText(['us-east-1','eu-west-2','ap-south-1','canary','rollback point'][i],bx+110,by+272+i*52);c.fillStyle='#2f9e5d';c.fillText('healthy',bx+bw-200,by+272+i*52)}
  cursor(c,t>28?bx+bw-60:bx+bw-240,t>28?by-10:by+300);
 }
 c.restore();
}
function field(c,x,y,label,val,focus,pw){c.fillStyle='#55554f';c.font='500 15px Plex';c.fillText(label,x,y);
 c.fillStyle='#fff';rr(c,x,y+12,380,48,8);c.fill();c.strokeStyle=focus?'#3b6cf0':'#d4d4ce';c.lineWidth=focus?3:2;c.stroke();
 c.fillStyle='#1c1c1a';c.font=(pw?'18px PlexMono':'17px Plex');c.fillText(val,x+16,y+43);
 if(pw){c.fillStyle='#7a7a74';c.font='14px Plex';c.fillText('Show',x+330,y+42)}}
function spinner(c,x,y,t){for(let i=0;i<8;i++){c.fillStyle=`rgba(59,108,240,${(i+1)/8})`;const a=i/8*6.283+t*3;c.beginPath();c.arc(x+Math.cos(a)*20,y+Math.sin(a)*20,4,0,7);c.fill()}}
function cursor(c,x,y){c.fillStyle='#111';c.strokeStyle='#fff';c.lineWidth=2;c.beginPath();c.moveTo(x,y);c.lineTo(x,y+26);c.lineTo(x+7,y+20);c.lineTo(x+18,y+20);c.closePath();c.fill();c.stroke()}
function rr(c,x,y,w,h,r){c.beginPath();c.roundRect(x,y,w,h,r)}
