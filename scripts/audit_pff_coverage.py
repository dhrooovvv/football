import bz2,json,re,concurrent.futures
from pathlib import Path
from collections import Counter
R=Path('experiments/pff-intake');D=Path('data/pff/release/Tracking Data');decoder=json.JSONDecoder();period_re=re.compile(r'"period"\s*:\s*(null|\d+)');frame_re=re.compile(r'"frameNum"\s*:\s*(\d+)');event_re=re.compile(r'"game_event"\s*:\s*');alive={'FIRSTKICKOFF','SECONDKICKOFF','THIRDKICKOFF','FOURTHKICKOFF','OTB'};known=alive|{'OUT','END','G','OFF','ON','SUB','VID'}
def audit(p):
 counts=Counter();events=Counter();priorperiod=None;state=None;owner=None;prev=None;nonmonotonic=0;total=0
 with bz2.open(p,'rt') as f:
  for line in f:
   total+=1;pa=period_re.search(line);fa=frame_re.search(line);period=int(pa.group(1)) if pa and pa.group(1)!='null' else None;frame=int(fa.group(1)) if fa else None
   if frame is None or (prev is not None and frame<=prev):nonmonotonic+=1
   prev=frame
   if period!=priorperiod:state=None;owner=None;priorperiod=period
   em=event_re.search(line);event=decoder.raw_decode(line[em.end():])[0] if em else None
   if event:
    code=event.get('game_event_type');events[str(code)]+=1
    if code in {'OUT','END'}:state='D'
    elif code in alive:state='live'
    elif code=='VID':state=None
    val=event.get('home_ball')
    if isinstance(val,bool):owner='H' if val else 'A'
   if period in (1,2):counts[state if state=='D' else owner if state=='live' and owner else 'X']+=1
 result={'match':p.name.split('.')[0],'all_frames':total,'standard_time_frames':sum(counts.values()),'state_counts':dict(counts),'annotated_fraction':1-counts['X']/sum(counts.values()) if sum(counts.values()) else None,'nonmonotonic_frame_count':nonmonotonic,'event_type_occurrences':dict(events),'unknown_event_types':sorted(set(events)-known)}
 print('Audited',result['match'],flush=True);return result

def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(audit,sorted(D.glob('*.bz2'))))
 (R/'coverage.json').write_text(json.dumps(rows,indent=2));print('Full64-match native state audit completed.',flush=True)
if __name__=='__main__':main()
