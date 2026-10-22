"""Stage 7: rule-based N-timing advisory (leaching/runoff risk from rain after application)"""
import json,datetime as dt,pathlib
R=pathlib.Path(__file__).parent.parent;D=R/'docs/data';cfg=json.load(open(R/'config/config.json'));W=json.load(open(D/'weather.json'))
rain={w['date']:w['rain'] for w in W};hz=dt.date.fromisoformat(W[-1]['date']);today=dt.date.today()
def r(d,n):return sum(rain.get((d+dt.timedelta(i)).isoformat(),0) for i in range(n))
def risk(a,b):return 'HIGH' if a>=25 or b>=40 else 'MODERATE' if a>=10 or b>=25 else 'LOW'
sow=dt.date.fromisoformat(cfg['sowing_date']);rows=[]
for a in cfg['n_plan']:
    t=sow+dt.timedelta(a['das']);w=a['window']
    c=[t+dt.timedelta(i) for i in range(-w,w+1)];c=[d for d in c if today<=d<=hz-dt.timedelta(2)]
    if t+dt.timedelta(w)<today:st,b='DONE',t
    elif not c:st,b='PROVISIONAL',t
    else:st,b='FORECAST',min(c,key=lambda d:(r(d,2)+.5*r(d,3),abs((d-t).days)))
    k=risk(r(b,2),r(b,3))
    act='Apply' if k=='LOW' else 'Split dose / delay' if k=='MODERATE' else 'Hold - heavy rain expected'
    rows.append(dict(stage=a['stage'],kg_n=a['kg_n'],target=str(t),best=str(b),rain48=round(r(b,2),1),rain72=round(r(b,3),1),risk=k,status=st,action=act if st!='DONE' else '-'))
daily=[dict(date=d,rain=rain[d],risk=risk(r(dt.date.fromisoformat(d),2),r(dt.date.fromisoformat(d),3))) for d in sorted(rain) if d>=str(today)]
json.dump(dict(plan=rows,daily=daily),open(D/'advisory.json','w'),indent=1)
