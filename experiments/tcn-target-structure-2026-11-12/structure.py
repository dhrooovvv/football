"""Label-free aggregate geometry diagnostics. No model, labels or identity repair."""
from collections import Counter
import numpy as np

QUANTILES = (.5, .9, .95, .99)
DISPLACEMENT_BINS_M = (0., .25, .5, 1., 2., 5., 10., 20., float('inf'))
CLOSE_PAIR_M = (.1, .5, 1.)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fraction(numerator, denominator):
    return numerator / denominator if denominator else None


class Distances:
    """Bounded-memory0.01m histogram; quantiles are intervals, not exact values."""
    def __init__(self):
        self.histogram = np.zeros(20001, np.int64)  # last bucket is >=200m
        self.bins = np.zeros(len(DISPLACEMENT_BINS_M)-1, np.int64)
        self.count = 0; self.total = 0.; self.minimum = None; self.maximum = None

    def add(self, values):
        values = np.asarray(values, dtype=np.float64).reshape(-1)
        require(np.isfinite(values).all() and (values >= 0).all(), 'Invalid distance observations')
        if not len(values):
            return
        self.count += len(values); self.total += float(values.sum())
        low, high = float(values.min()), float(values.max())
        self.minimum = low if self.minimum is None else min(self.minimum,low)
        self.maximum = high if self.maximum is None else max(self.maximum,high)
        indices = np.minimum(np.floor(values * 100),20000).astype(np.int64)
        self.histogram += np.bincount(indices,minlength=20001)
        self.bins += np.histogram(values, bins=DISPLACEMENT_BINS_M)[0]

    def result(self):
        cumulative = self.histogram.cumsum()
        quantiles = {}
        for q in QUANTILES:
            if self.count:
                index = int(np.searchsorted(cumulative,max(1,int(np.ceil(q*self.count)))))
                quantiles[str(q)] = [index / 100, (index+1)/100 if index < 20000 else None]
            else:
                quantiles[str(q)] = None
        return dict(count=int(self.count),mean_m=fraction(self.total,self.count),min_m=self.minimum,
                    max_m=self.maximum,quantile_intervals_m=quantiles,histogram_resolution_m=.01,
                    descriptive_bins_m=[dict(lower_m=left,upper_m=right if np.isfinite(right) else None,
                        count=int(count),share=fraction(int(count),self.count))
                        for left,right,count in zip(DISPLACEMENT_BINS_M,DISPLACEMENT_BINS_M[1:],self.bins)])


class Runs:
    """Exact pooled visible/missing run lengths, reset at real half boundaries."""
    def __init__(self, slots, fps):
        self.lengths=np.zeros(slots,np.int64);self.states=np.zeros(slots,bool)
        self.counts={True:Counter(),False:Counter()};self.fps=fps
        self.appearances=0;self.disappearances=0

    def add(self, mask):
        for slot in range(mask.shape[1]):
            column=mask[:,slot];changes=np.flatnonzero(column[1:]!=column[:-1])+1
            self.appearances += int(column[changes].sum())
            self.disappearances += len(changes)-int(column[changes].sum())
            starts=np.r_[0,changes];stops=np.r_[changes,len(column)]
            lengths=stops-starts;states=column[starts]
            if self.lengths[slot]:
                if self.states[slot] == states[0]:
                    lengths[0]+=self.lengths[slot]
                else:
                    self.counts[bool(self.states[slot])][int(self.lengths[slot])]+=1
                    if states[0]: self.appearances+=1
                    else: self.disappearances+=1
            for state,length in zip(states[:-1],lengths[:-1]):
                self.counts[bool(state)][int(length)]+=1
            self.states[slot]=states[-1];self.lengths[slot]=lengths[-1]

    def finish_block(self):
        for state,length in zip(self.states,self.lengths):
            if length: self.counts[bool(state)][int(length)]+=1
        self.lengths[:]=0

    def result(self):
        require(not self.lengths.any(), 'Finish half before reporting runs')
        result=dict(appearances_after_observed_absence=int(self.appearances),
                    disappearances_after_observed_presence=int(self.disappearances),
                    includes_half_edge_censored_fragments=True)
        for state,name in ((True,'visible_runs'),(False,'missing_runs')):
            counts=self.counts[state];total=sum(counts.values());frames=sum(k*v for k,v in counts.items())
            quantiles={}
            for q in QUANTILES:
                rank=max(1,int(np.ceil(q*total)));cumulative=0;value=None
                for length,count in sorted(counts.items()):
                    cumulative+=count
                    if cumulative>=rank:
                        value=length/self.fps;break
                quantiles[str(q)]=value
            result[name]=dict(count=total,mean_seconds=fraction(frames,total*self.fps),
                             max_seconds=max(counts)/self.fps if counts else None,
                             quantiles_seconds=quantiles)
        return result


def summarize(frames, teams, blocks, pitch_metres, read_chunk, fps=25, chunk_size=256):
    """read_chunk(a,b) returns only normalizedXYfloat32 and visibleboolean arrays.

    No pair spans a real half. Nearest set distance is directed/many-to-one,
    never an assignment or inferred identity. No time series escape this call.
    """
    teams=np.asarray(teams)
    pitch=np.asarray(pitch_metres,dtype=np.float64)
    require(teams.ndim==1 and set(teams.tolist())=={0,1}, 'Require explicit two-team mapping')
    require(pitch.shape==(2,) and np.isfinite(pitch).all() and (pitch>0).all(), 'Invalid physical pitch scale')
    require(fps==25 and isinstance(chunk_size,int) and chunk_size>0, 'Frozen25Hz/chunk contract differs')
    previous=0
    for start,stop in blocks:
        require(previous<=start<stop<=frames, 'Invalid real half blocks');previous=stop
    require(bool(blocks), 'No half blocks')
    metrics={}
    for team in (0,1):
        slots=np.flatnonzero(teams==team)
        metrics[team]=dict(slots=slots,same_slot=Distances(),nearest_set=Distances(),nearest_paired=Distances(),
                           runs=Runs(len(slots),fps),coverage=np.zeros(len(slots)+1,np.int64),
                           clipped_pairs=0,clipped_components=0,transition_pairs=0,pair_count=0,
                           close_pairs={threshold:0 for threshold in (0.,*CLOSE_PAIR_M)},
                           close_frames={threshold:0 for threshold in (0.,*CLOSE_PAIR_M)})
    active_frames=0
    for begin,end in blocks:
        last_xy,last_seen=None,None
        for start in range(begin,end,chunk_size):
            stop=min(end,start+chunk_size)
            xy,seen=read_chunk(start,stop)
            xy=np.asarray(xy);seen=np.asarray(seen)
            require(xy.shape==(stop-start,len(teams),2) and xy.dtype==np.float32
                    and seen.shape==xy.shape[:-1] and seen.dtype==np.bool_, 'Invalid normalized geometry chunk')
            require(np.isfinite(xy[seen]).all(), 'Visible coordinates must be finite')
            # Missing coordinates never participate in distances or normalized velocity.
            xy=np.where(seen[:,:,None],xy,0)
            prior_xy=np.concatenate([last_xy[None],xy[:-1]]) if last_xy is not None else xy[:-1]
            prior_seen=np.concatenate([last_seen[None],seen[:-1]]) if last_seen is not None else seen[:-1]
            current_xy=xy if last_xy is not None else xy[1:]
            current_seen=seen if last_seen is not None else seen[1:]
            active_frames+=stop-start
            for team in (0,1):
                value=metrics[team];slots=value['slots'];mask=seen[:,slots]
                counts=mask.sum(1);value['coverage']+=np.bincount(counts,minlength=len(slots)+1)
                value['runs'].add(mask)
                # Per-frame exact/close pair counts use upper triangle once per unordered pair.
                position=xy[:,slots]*pitch
                distances=np.linalg.norm(position[:,:,None]-position[:,None,:],axis=-1)
                valid=mask[:,:,None]&mask[:,None,:]&np.triu(np.ones((len(slots),len(slots)),bool),k=1)
                value['pair_count']+=int(valid.sum())
                for threshold in (0.,*CLOSE_PAIR_M):
                    close=valid&(distances<=threshold)
                    value['close_pairs'][threshold]+=int(close.sum())
                    value['close_frames'][threshold]+=int(close.any(axis=(1,2)).sum())
                if not len(current_xy):
                    continue
                now,before=current_xy[:,slots],prior_xy[:,slots]
                now_seen,before_seen=current_seen[:,slots],prior_seen[:,slots]
                paired=now_seen&before_seen
                delta=now-before
                value['same_slot'].add(np.linalg.norm((now.astype(np.float64)-before.astype(np.float64))*pitch,
                                                       axis=-1)[paired])
                velocity=delta*np.float32(fps)
                clipping=(np.abs(velocity)>5)&paired[:,:,None]
                value['transition_pairs']+=int(paired.sum())
                value['clipped_pairs']+=int(clipping.any(2).sum())
                value['clipped_components']+=int(clipping.sum())
                set_distance=np.linalg.norm((now.astype(np.float64)[:,:,None]
                                            -before.astype(np.float64)[:,None,:])*pitch,axis=-1)
                set_distance=np.where(before_seen[:,None,:],set_distance,np.inf)
                nearest=set_distance.min(2)
                supported=now_seen&before_seen.any(1)[:,None]
                value['nearest_set'].add(nearest[supported])
                value['nearest_paired'].add(nearest[paired])
            last_xy,last_seen=xy[-1].copy(),seen[-1].copy()
        for value in metrics.values():value['runs'].finish_block()
    result=dict(active_frames=active_frames,fps=fps,real_half_count=len(blocks),pitch_metres=pitch.tolist(),teams={})
    for team,name in ((0,'H'),(1,'A')):
        value=metrics[team];coverage=value['coverage'];pairs=value['transition_pairs']
        result['teams'][name]=dict(allocated_player_slots=len(value['slots']),
            visible_slot_count=dict(mean=float(np.dot(np.arange(len(coverage)),coverage)/active_frames),
                frequency={str(i):int(n) for i,n in enumerate(coverage)},
                frames_fewer_than_11=int(coverage[:11].sum()),frames_more_than_11=int(coverage[12:].sum()),
                frames_zero_visible=int(coverage[0])),
            adjacent_observed_same_slot_displacement=value['same_slot'].result(),
            directed_nearest_same_team_previous_set=value['nearest_set'].result(),
            nearest_previous_set_for_same_slot_observed_pairs=value['nearest_paired'].result(),
            encoder_velocity_clipping_proxy=dict(adjacent_observed_pairs=pairs,
                any_component_exceeds_abs5_count=value['clipped_pairs'],
                any_component_exceeds_abs5_fraction=fraction(value['clipped_pairs'],pairs),
                components_exceed_abs5_count=value['clipped_components'],
                components_exceed_abs5_fraction=fraction(value['clipped_components'],2*pairs)),
            observation_runs=value['runs'].result(),
            same_team_close_position_proxies=dict(visible_unordered_pair_count=value['pair_count'],
                thresholds=[dict(distance_at_most_m=threshold,pair_count=value['close_pairs'][threshold],
                    pair_fraction=fraction(value['close_pairs'][threshold],value['pair_count']),
                    frames_any_pair=value['close_frames'][threshold],
                    frame_fraction=fraction(value['close_frames'][threshold],active_frames))
                    for threshold in (0.,*CLOSE_PAIR_M)]))
    return result
