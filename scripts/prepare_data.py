"""Run from repository root with PYTHONPATH=src. Never prints restricted values."""
import argparse
import json
from pathlib import Path
import subprocess
from possession.archive import extract_bundle
from possession.inputs import load_atd, load_homography, load_tags, load_teams


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--source', choices=['tactical', 'broadcast'])
    parser.add_argument('--config', type=Path, default=Path('configs/competition.json'))
    parser.add_argument('--root', type=Path, default=Path('data/competition'))
    args = parser.parse_args()
    if args.archive:
        extract_bundle(args.archive, args.root)
    config = json.loads(args.config.read_text())
    report = {'checks': {}, 'missing': []}
    for source, spec in config['sources'].items():
        if args.source and args.source != source:
            continue
        slots, frames = spec['slots'], spec['frames']
        prefix = args.root / source / ('BAR-ATH_' + source)
        for suffix, validator in [('_atd.txt',lambda p:load_atd(p,frames,slots)),('_homography.csv',lambda p:load_homography(p,frames))]:
            path = Path(str(prefix)+suffix)
            key=source+suffix
            if not path.exists():
                report['missing'].append(path.name)
                continue
            try:
                validator(path)
                report['checks'][key] = 'pass'
            except Exception as error:
                # Do not copy exception messages: third-party parsers may include asset contents.
                report['checks'][key] = 'fail:' + type(error).__name__
        if source == 'tactical':
            tags_path = Path(str(prefix) + '_smart_tagging.xml')
            if tags_path.exists():
                try:
                    load_tags(tags_path, frames, config['fps'])
                    report['checks']['tactical_smart_tagging.xml'] = 'pass'
                except Exception as error:
                    report['checks']['tactical_smart_tagging.xml'] = 'fail:' + type(error).__name__
        meta_path = Path(str(prefix) + '_atd.xml')
        if meta_path.exists():
            try:
                load_teams(meta_path, slots, config['home_team'], config['away_team'])
                report['checks'][source + '_atd.xml'] = 'pass'
            except Exception as error:
                report['checks'][source + '_atd.xml'] = 'fail:' + type(error).__name__
        required = ['_atd.xml'] + (['_smart_tagging.xml'] if source=='tactical' else [])
        for suffix in required:
            if not Path(str(prefix)+suffix).exists(): report['missing'].append(prefix.name+suffix)
    video=args.root/'tactical/BAR-ATH_tactical.mp4'
    if args.source == "broadcast":
        pass
    elif video.exists():
        result=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration','-of','json',str(video)],capture_output=True,text=True)
        (args.root/'video-header.json').write_text(result.stdout)
        if result.returncode:
            report['checks']['tactical_video_header']='fail'
        else:
            streams=json.loads(result.stdout).get('streams',[])
            report['checks']['tactical_video_alignment']='pass' if len(streams)==1 and streams[0].get('nb_frames')=='199319' and streams[0].get('avg_frame_rate')=='25/1' else 'mismatch_or_unknown'
    else: report['missing'].append('BAR-ATH_tactical.mp4')
    report['team_features']='blocked_missing_metadata' if 'BAR-ATH_tactical_atd.xml' in report['missing'] else 'not_run'
    (args.root / ('validation-' + args.source + '.json' if args.source else 'validation.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
