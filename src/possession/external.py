"""Strict IDSSE/DFL adapter. Labels are returned separately from observations."""
import xml.etree.ElementTree as ET
from datetime import datetime
import numpy as np
from .inputs import Tracking


def load_match(metadata, positions):
    root=ET.parse(metadata).getroot()
    general=next(root.iter('General')); env=next(root.iter('Environment'))
    ids=[general.get('HomeTeamId'),general.get('AwayTeamId') or general.get('GuestTeamId')]
    if None in ids or ids[0]==ids[1]: raise ValueError('Invalid team IDs')
    pitch=np.array([float(env.get('PitchX')),float(env.get('PitchY'))])
    sets={}
    for _,node in ET.iterparse(positions,events=('end',)):
        if node.tag!='FrameSet': continue
        team=node.get('TeamId'); half=node.get('GameSection')
        if team and team.lower()=='ball': team='ball'
        if team not in ids+['ball'] or half not in ['firstHalf','secondHalf']:
            node.clear();continue
        key=(half,team,node.get('PersonId'))
        if key in sets: raise ValueError('Duplicate frame set')
        frames=list(node)
        n=np.array([int(f.get('N')) for f in frames])
        if len(n)==0 or (np.diff(n)!=1).any(): raise ValueError('Nonsequential external frames')
        xy=np.array([[float(f.get('X')),float(f.get('Y')),np.nan] for f in frames])
        if np.isinf(xy).any(): raise ValueError('Infinite coordinates')
        labels=None
        if team=='ball':
            if len(frames)>1 and abs((datetime.fromisoformat(frames[1].get('T'))-datetime.fromisoformat(frames[0].get('T'))).total_seconds()-.04)>1e-6: raise ValueError('Expected 25Hz')
            status=np.array([int(f.get('BallStatus')) for f in frames]); owner=np.array([int(f.get('BallPossession')) for f in frames])
            labels=np.full(len(n),'X');labels[status==0]='D';labels[(status==1)&(owner==1)]='H';labels[(status==1)&(owner==2)]='A'
        sets[key]=(n,xy,labels);node.clear()
    players=sorted({(k[1],k[2]) for k in sets if k[1]!='ball'})
    teams=np.array([ids.index(t) for t,_ in players]);parts=[];balls=[];ys=[];blocks=[];offset=0
    for half in ['firstHalf','secondHalf']:
        ballsets=[v for k,v in sets.items() if k[0]==half and k[1]=='ball']
        if len(ballsets)!=1: raise ValueError('Missing/duplicate ball half')
        n,b,y=ballsets[0];p=np.full((len(n),len(players),3),np.nan)
        for j,(t,person) in enumerate(players):
            key=(half,t,person)
            if key not in sets: continue
            pn,px,_=sets[key];idx=pn-n[0]
            if (idx<0).any() or (idx>=len(n)).any(): raise ValueError('Player outside ball timeline')
            p[idx,j]=px
        p[...,:2]=p[...,:2]/pitch+.5;b[:,:2]=b[:,:2]/pitch+.5
        parts.append(p);balls.append(b);ys.append(y);blocks.append((offset,offset+len(n)));offset+=len(n)
    return Tracking(np.concatenate(parts),np.concatenate(balls)),teams,blocks,pitch,np.concatenate(ys)
