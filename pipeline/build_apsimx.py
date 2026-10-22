"""Stage 3: patch APSIM rice template (clock, weather, sowing) -> ClimSmart-Rice.apsimx"""
import json,glob,shutil,datetime as dt,pathlib
R=pathlib.Path(__file__).parent.parent;cfg=json.load(open(R/'config/config.json'));W=json.load(open(R/'work/weather.json'))
t=R/'work/template.apsimx'
own=R/'assets/template/Rice.apsimx'
if own.exists():shutil.copy(own,t)
else:
    c=[p for p in glob.glob('/tmp/apsim/src/**/*.apsimx',recursive=True) if 'rice' in p.lower()]
    c.sort(key=lambda p:(not p.lower().endswith('/rice.apsimx'),len(p)));print('template candidates:',*c,sep='\n  ')
    if not c:raise SystemExit('No rice template found: put one at assets/template/Rice.apsimx')
    shutil.copy(c[0],t);print('using',c[0])
m=json.load(open(t))
s=dt.date.fromisoformat(W[0]['date']);e=min(dt.date.fromisoformat(cfg['sowing_date'])+dt.timedelta(days=cfg['duration_days']),dt.date.fromisoformat(W[-1]['date']))
def walk(n):
    ty=n.get('$type','')
    if ty.startswith('Models.Climate.Weather'):n['FileName']='weather.met'
    elif ty.startswith('Models.Clock'):n['Start']=f'{s}T00:00:00';n['End']=f'{e}T00:00:00'
    elif ty.startswith('Models.Manager'):
        for p in n.get('Parameters') or []:
            if p.get('Key') in cfg['overrides']:p['Value']=cfg['overrides'][p['Key']]
    for c in n.get('Children',[]):walk(c)
walk(m);json.dump(m,open(R/'work/ClimSmart-Rice.apsimx','w'),indent=1);print('built',s,e)
