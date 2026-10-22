"""Stage 5-6: APSIM .db -> output.json, meta.json; copy inputs to docs/data"""
import json,sqlite3,shutil,datetime as dt,pathlib
R=pathlib.Path(__file__).parent.parent;D=R/'docs/data';D.mkdir(parents=True,exist_ok=True)
c=sqlite3.connect(R/'work/ClimSmart-Rice.db');out={}
for (n,) in c.execute("select name from sqlite_master where type='table' and name not like '\\_%' escape '\\'"):
    cur=c.execute(f'select * from "{n}"');out[n]=dict(columns=[d[0] for d in cur.description],rows=cur.fetchall())
json.dump(out,open(D/'output.json','w'))
shutil.copy(R/'work/weather.json',D/'weather.json');shutil.copy(R/'assets/polygon.geojson',D/'polygon.json');shutil.copy(R/'config/config.json',D/'config.json')
json.dump(dict(run_at=dt.datetime.utcnow().isoformat(timespec='seconds')+'Z',tables={k:len(v['rows']) for k,v in out.items()}),open(D/'meta.json','w'))
