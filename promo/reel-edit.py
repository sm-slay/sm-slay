import subprocess, os, sys
SRC=sys.argv[1]; OUT=sys.argv[2]; B=os.path.join(os.path.dirname(OUT),'build')
BOLD='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
REG='/usr/share/fonts/opentype/inter/Inter-Medium.otf'
W,H=1080,1920; BG='0x0d1120'
# (name, start, dur, speed, crop(w,h,x,y), caption lines, sub, blurs[(x,y,w,h,t0,t1)] in source coords/time)
CARD=(980,522,140,30)
SEGS=[
 ('hook',0.0,2.0,1.0,(1180,740,160,0),["We built a local auto","shop its own CRM."],"Whisnant's Automotive · NC",[CARD+(0,99)]),
 ('form',13.0,8.5,2.5,(760,722,572,78),["New call comes in?","Logged in seconds."],"Name, car, repair, who's handling it",[(590,200,360,48,0,99),(955,200,360,48,0,99)]),
 ('save',22.4,1.6,1.2,(760,722,572,78),["Hit save..."],"",[]),
 ('board',24.0,3.0,1.0,(820,470,930,255),["...and it's on the board.","Both guys see it."],"Synced between the counter and the bays",[CARD+(0,99)]),
 ('tabs',34.2,4.6,1.4,(960,640,160,80),["Customers. Appointments.","Follow-ups. One place."],"No more sticky notes",[(170,488,420,60,34.2,37.8)]),
]
def esc(s): return s.replace("\\","\\\\").replace("'","’").replace(":","\\:").replace(",","\\,").replace("%","\\%")
parts=[]
for i,(n,st,du,sp,(cw,ch,cx,cy),cap,sub,blurs) in enumerate(SEGS):
    pw=W-80; ph=round(ch*pw/cw); py=640 if ph<700 else 560
    f=f"[0:v]trim=start={st}:duration={du},setpts=PTS-STARTPTS,fps=30[v0];"
    cur='v0'
    for j,(bx,by,bw,bh,t0,t1) in enumerate(blurs):
        lt0=max(0,t0-st)
        f+=f"[{cur}]split[a{j}][b{j}];[b{j}]crop={bw}:{bh}:{bx}:{by},gblur=sigma=9:steps=3[bb{j}];[a{j}][bb{j}]overlay={bx}:{by}:enable='between(t,{lt0},{t1-st})'[o{j}];"
        cur=f'o{j}'
    f+=f"[{cur}]crop={cw}:{ch}:{cx}:{cy},scale={pw}:{ph}:flags=lanczos,setpts=PTS/{sp}[p];"
    f+=f"color=c={BG}:s={W}x{H}:r=30[bg];[bg][p]overlay=40:{py}:shortest=1,format=yuv420p"
    y=py-60-len(cap)*88
    for k,l in enumerate(cap):
        f+=f",drawtext=fontfile={BOLD}:text='{esc(l)}':fontsize=76:fontcolor=white:x=(w-text_w)/2:y={y+k*92}"
    if sub: f+=f",drawtext=fontfile={REG}:text='{esc(sub)}':fontsize=40:fontcolor=0xa9b0cc:x=(w-text_w)/2:y={py+ph+56}"
    f+=f",drawtext=fontfile={BOLD}:text='sitralmarketing.com':fontsize=34:fontcolor=0xff6b4a:x=(w-text_w)/2:y=1780"
    out=f"{B}/{i}_{n}.mp4"
    subprocess.run(['ffmpeg','-v','error','-y','-i',SRC,'-filter_complex',f,'-an','-c:v','libx264','-crf','18','-preset','medium','-r','30',out],check=True)
    parts.append(out)
# end card
end=f"{B}/9_end.mp4"
f=(f"color=c={BG}:s={W}x{H}:r=30:d=3,format=yuv420p,"
   f"drawtext=fontfile={BOLD}:text='Run a shop?':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=720,"
   f"drawtext=fontfile={BOLD}:text='We’ll build yours.':fontsize=96:fontcolor=white:x=(w-text_w)/2:y=830,"
   f"drawtext=fontfile={BOLD}:text='sitralmarketing.com':fontsize=60:fontcolor=0xff6b4a:x=(w-text_w)/2:y=1010")
subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f,'-c:v','libx264','-crf','18','-r','30',end],check=True)
parts.append(end)
lst=f"{B}/list.txt"; open(lst,'w').write(''.join(f"file '{p}'\n" for p in parts))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',lst,'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',OUT],check=True)
