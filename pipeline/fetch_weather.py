"""Stage 1-2: polygon -> centroid -> Open-Meteo -> APSIM .met + weather.json"""
import json,datetime as dt,requests,pathlib
R=pathlib.Path(__file__).parent.parent;(R/'work').mkdir(exist_ok=True)
cfg=json.load(open(R/'config/config.json'));poly=json.load(open(R/'assets/polygon.geojson'))
ring=poly['features'][0]['geometry']['coordinates'][0][:-1]
lon=sum(p[0] for p in ring)/len(ring);lat=sum(p[1] for p in ring)/len(ring)
today=dt.date.today();start=dt.date.fromisoformat(cfg['sowing_date'])-dt.timedelta(days=cfg['pre_sowing_days'])
V='temperature_2m_max,temperature_2m_min,shortwave_radiation_sum,precipitation_sum'
def get(url,**p):
    r=requests.get(url,params=dict(latitude=lat,longitude=lon,daily=V,timezone='auto',**p),timeout=60);r.raise_for_status();return r.json()['daily']
rows={}
def add(d):
    for i,t in enumerate(d['time']):
        v=[d[k][i] for k in V.split(',')]
        if None not in v:rows[t]=v
a_end=today-dt.timedelta(days=6)
if start<=a_end:add(get('https://archive-api.open-meteo.com/v1/archive',start_date=str(start),end_date=str(a_end)))
add(get('https://api.open-meteo.com/v1/forecast',past_days=7,forecast_days=16))
real=set(rows);end=dt.date.fromisoformat(cfg['sowing_date'])+dt.timedelta(days=cfg['duration_days']);last=dt.date.fromisoformat(max(rows))
if end>last:  # beyond forecast horizon: 3-year daily climatology
    cl=get('https://archive-api.open-meteo.com/v1/archive',start_date=f'{today.year-3}-01-01',end_date=f'{today.year-1}-12-31');acc={}
    for i,t in enumerate(cl['time']):
        v=[cl[k][i] for k in V.split(',')]
        if None not in v:acc.setdefault(t[5:],[]).append(v)
    d=last+dt.timedelta(1)
    while d<=end:
        a=acc.get(d.strftime('%m-%d')) or acc.get('02-28')
        if a:rows[str(d)]=[sum(c)/len(a) for c in zip(*a)]
        d+=dt.timedelta(1)
days=[d for d in sorted(rows) if d>=str(start)]
tm=[(rows[d][0]+rows[d][1])/2 for d in days];tav=sum(tm)/len(tm)
mo={}
for d,t in zip(days,tm):mo.setdefault(d[:7],[]).append(t)
mm=[sum(v)/len(v) for v in mo.values()];amp=(max(mm)-min(mm)) if len(mm)>1 else 2.0
L=['[weather.met.weather]',f'!ClimSmart-Rice | Open-Meteo | {lat:.4f},{lon:.4f}',f'latitude = {lat:.4f}',f'longitude = {lon:.4f}',f'tav = {tav:.2f}',f'amp = {amp:.2f}','year day radn maxt mint rain','() () (MJ/m2) (oC) (oC) (mm)']
W=[]
for d in days:
    x=dt.date.fromisoformat(d);mx,mn,rad,rn=rows[d]
    L.append(f'{x.year} {x.timetuple().tm_yday} {rad:.2f} {mx:.1f} {mn:.1f} {rn:.1f}');W.append(dict(date=d,maxt=mx,mint=mn,radn=rad,rain=rn,f=int(d in real)))
(R/'work/weather.met').write_text('\n'.join(L)+'\n');json.dump(W,open(R/'work/weather.json','w'))
print(f'{len(W)} days @ {lat:.4f},{lon:.4f}')
