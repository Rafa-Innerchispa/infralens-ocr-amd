#!/usr/bin/env python3
"""Generate deterministic challenge-like OCR fixtures plus exact expected text."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

OUT=Path("var/mc2_fixtures")
OUT.mkdir(parents=True,exist_ok=True)

def font(size:int,bold:bool=False):
    candidates=[
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path,size)
        except OSError:
            pass
    return ImageFont.load_default()

def centered(draw,text,box,fnt,fill="black"):
    x0,y0,x1,y1=box
    b=draw.textbbox((0,0),text,font=fnt)
    w,h=b[2]-b[0],b[3]-b[1]
    draw.text((x0+(x1-x0-w)/2,y0+(y1-y0-h)/2),text,font=fnt,fill=fill)

expected={}

# US plate with distracting state banner.
img=Image.new("RGB",(900,420),"white")
d=ImageDraw.Draw(img)
d.rounded_rectangle((55,55,845,365),radius=35,outline="black",width=8)
centered(d,"CALIFORNIA",(80,65,820,140),font(42,True))
centered(d,"8ABC123",(80,135,820,315),font(104,True))
centered(d,"dmv.ca.gov",(100,305,800,350),font(26))
img.save(OUT/"us_plate_state.png")
expected["us_plate_state.png"]="8ABC123"

# Slightly degraded plate.
img=Image.new("RGB",(920,420),(225,225,220))
d=ImageDraw.Draw(img)
d.rounded_rectangle((55,55,865,365),radius=28,fill=(242,242,232),outline="black",width=6)
centered(d,"NEVADA",(100,70,820,135),font(38,True))
centered(d,"5KLM921",(95,135,825,310),font(100,True))
img=ImageEnhance.Contrast(img).enhance(0.82).filter(ImageFilter.GaussianBlur(1.15))
img.save(OUT/"plate_blur.jpg",quality=68)
expected["plate_blur.jpg"]="5KLM921"

def sign(name,lines,expected_text,size=(900,700),blur=0.0,quality=92):
    img=Image.new("RGB",size,"white")
    d=ImageDraw.Draw(img)
    d.rectangle((55,55,size[0]-55,size[1]-55),outline="black",width=18)
    line_h=(size[1]-150)//len(lines)
    for i,line in enumerate(lines):
        centered(d,line,(90,80+i*line_h,size[0]-90,80+(i+1)*line_h),font(min(92,line_h-10),True))
    if blur:
        img=img.filter(ImageFilter.GaussianBlur(blur))
    path=OUT/name
    img.save(path,quality=quality)
    expected[name]=expected_text

sign("road_work_ahead.png",["ROAD","WORK","AHEAD"],"ROAD WORK AHEAD")
sign("speed_limit_65.png",["SPEED","LIMIT","65"],"SPEED LIMIT 65")
sign("advisory_35.jpg",["35","MPH"],"35",blur=0.45,quality=82)
sign("road_closed_large.jpg",["ROAD","CLOSED","AHEAD"],"ROAD CLOSED AHEAD",size=(3000,2200),quality=80)

(OUT/"expected.json").write_text(json.dumps(expected,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps({"output":str(OUT),"cases":len(expected),"expected":expected},indent=2))
