"""Strict PFF native grouping and conservative25Hz conversion. No modelling."""
import bz2,json
from pathlib import Path
import numpy as np
from .inputs import Tracking
ALIVE={'FIRSTKICKOFF','SECONDKICKOFF','THIRDKICKOFF','FOURTHKICKOFF','OTB','G'}
NEUTRAL={'CLK','OFF','ON','SUB'}

def consensus(values):
 a=np.asarray([[np.nan,np.nan] if v is None else v for v in values],float)
 if a.shape!=(len(values),2) or np.isinf(a).any():raise ValueError('Invalid observation shape/infinity')
 return a[0] if np.isfinite(a).all() and np.array_equal(a,np.broadcast_to(a[0],a.shape)) else np.full(2,np.nan)

def event_state(events,state=None,owner=None):
 states=set();owners=set()
 for e in events:
  if not e:continue
  code=e.get('game_event_type')
  if code in ALIVE:states.add('live')
  elif code in {'OUT','END'}:states.add('D')
  elif code=='VID':states.add('unknown')
  elif code not in NEUTRAL:raise ValueError('Unsupported PFF event code')
  value=e.get('home_ball')
  if value is not None:
   if not isinstance(value,bool):raise ValueError('Expected boolean home_ball')
   owners.add('H' if value else 'A')
 if states:state=next(iter(states)) if len(states)==1 and 'unknown' not in states else None
 if owners:owner=next(iter(owners)) if len(owners)==1 else None
 if state is None:owner=None
 return state,owner,('D' if state=='D' else owner if state=='live' and owner else 'X')

def resample(times,players,ball,labels,fps):
 times=np.asarray(times,float)
 if not len(times) or not np.isfinite(times).all() or (np.diff(times)<=0).any():raise ValueError('PFF timestamps not increasing')
 grid=np.arange(int(np.ceil(times[0]*25-1e-8)),int(np.floor(times[-1]*25+1e-8))+1)/25
 right=np.searchsorted(times,grid);r=np.minimum(right,len(times)-1);l=np.maximum(right-1,0);near=np.where(np.abs(times[l]-grid)<=np.abs(times[r]-grid),l,r);observed=np.abs(times[near]-grid)<=.51/fps
 p=np.asarray(players)[near].copy();b=np.asarray(ball)[near].copy();p[~observed]=np.nan;b[~observed]=np.nan
 past=np.searchsorted(times,grid,side='right')-1;safe=np.maximum(past,0);valid=(past>=0)&((grid-times[safe])<=1/fps+1e-9);y=np.full(len(grid),'X');y[valid]=np.asarray(labels)[safe[valid]]
 return p,b,y,grid

def load_pff(root,match):
 root=Path(root);metadata=json.loads((root/'Metadata'/f'{match}.json').read_text());assert len(metadata)==1;m=metadata[0];fps=float(m['fps']);pitch=m['stadium']['pitches'][0];pitch=np.array([pitch['length'],pitch['width']],float)
 if not np.isfinite(pitch).all() or (pitch<=0).any() or fps<=0:raise ValueError('Invalid pitch/fps')
 roster=json.loads((root/'Rosters'/f'{match}.json').read_text());sides={m['homeTeam']['id']:0,m['awayTeam']['id']:1};slots={}
 for p in roster:
  team=p['team']['id'];key=(sides[team],int(p['shirtNumber']))
  if key in slots:raise ValueError('Duplicate roster team/jersey')
  slots[key]=len(slots)
 teams=np.array([k[0] for k in slots]);parts={1:[],2:[]};counts={'records':0,'unique_frames':0,'duplicate_records':0,'player_conflicts':0,'ball_conflicts':0,'event_association_only_duplicates':0};group=[];lastkey=None;prevframe={};prevtime={};state=None;owner=None
 def flush(g):
  nonlocal state,owner
  per=g[0]['period'];frame=g[0]['frameNum'];times=[float(x['videoTimeMs'])/1000 for x in g]
  if max(times)!=min(times):raise ValueError('Conflicting duplicate timestamps')
  time=times[0]
  if per in prevframe:
   if frame<=prevframe[per] or time<=prevtime[per]:raise ValueError('Nonincreasing unique frame/time')
   if abs((time-prevtime[per])-(frame-prevframe[per])/fps)>2/fps:raise ValueError('PFF video/frame clock mismatch')
  else:state=None;owner=None
  prevframe[per]=frame;prevtime[per]=time;observations=[]
  for row in g:
   positions={}
   for side,name in [(0,'homePlayersSmoothed'),(1,'awayPlayersSmoothed')]:
    for q in row.get(name) or []:
     key=(side,int(q['jerseyNum']))
     if key not in slots:raise ValueError('Unknown tracking jersey')
     positions.setdefault(key,[]).append([q.get('x'),q.get('y')])
   positions={k:consensus(v) for k,v in positions.items()}
   observations.append(positions)
  p=np.full((len(slots),3),np.nan);conflicts=0
  for key,j in slots.items():
   values=[q.get(key) for q in observations];p[j,:2]=consensus(values)
   if len(g)>1 and any(v is not None for v in values) and not np.isfinite(p[j,:2]).all():conflicts+=1
  bs=[q.get('ballsSmoothed') for q in g];ball=np.full(3,np.nan);ball[:2]=consensus([None if q is None else [q.get('x'),q.get('y')] for q in bs]);bc=int(len(g)>1 and any(q is not None for q in bs) and not np.isfinite(ball[:2]).all())
  counts['player_conflicts']+=conflicts;counts['ball_conflicts']+=bc;counts['unique_frames']+=1;counts['duplicate_records']+=len(g)-1
  if len(g)>1 and not conflicts and not bc:counts['event_association_only_duplicates']+=1
  state,owner,label=event_state([q.get('game_event') for q in g],state,owner);parts[per].append((time,p,ball,label))
 with bz2.open(root/'Tracking Data'/f'{match}.jsonl.bz2','rt') as f:
  for line in f:
   row=json.loads(line);counts['records']+=1
   if row.get('period') not in [1,2]:continue
   key=(row['period'],row['frameNum'])
   if group and key!=lastkey:flush(group);group=[]
   group.append(row);lastkey=key
 if group:flush(group)
 ps=[];bs=[];ys=[];blocks=[];offset=0
 for per in [1,2]:
  rows=parts[per]
  if not rows:raise ValueError('Missing standard half')
  time,p,b,y=zip(*rows);p,b,y,grid=resample(time,p,b,y,fps);p[...,:2]=p[...,:2]/pitch+.5;b[:,:2]=b[:,:2]/pitch+.5;ps.append(p);bs.append(b);ys.append(y);blocks.append((offset,offset+len(y)));offset+=len(y)
 return Tracking(np.concatenate(ps),np.concatenate(bs)),teams,blocks,pitch,np.concatenate(ys),counts
