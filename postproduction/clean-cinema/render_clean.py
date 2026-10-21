#!/usr/bin/env python3
"""Render the clean cinematic revision from the original source, not an export."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
import numpy as np
from clean_grade import grade_frame


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                              '-show_format', '-of', 'json', str(path)]))


def stabilized_frames(source, root, width, height):
    shots = [(0, 118, 'road-a'), (118, 200, 'road-b'), (200, 238, 'wall'),
             (238, 541, 'garden'), (541, 730, 'gate')]
    arrays = []
    environment = dict(os.environ, OMP_NUM_THREADS='2')
    stab_root = root / 'stabilization'
    stab_root.mkdir(exist_ok=True)
    for first, last, name in shots:
        transform = stab_root / f'{name}.trf'
        trim = f'trim=start_frame={first}:end_frame={last},setpts=PTS-STARTPTS'
        common = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-threads', '2',
                  '-filter_threads', '2', '-i', str(source)]
        with (stab_root / f'{name}.log').open('w') as log:
            subprocess.run(common + ['-vf', trim + ',vidstabdetect=shakiness=2:accuracy=9:'
                                    f'result={transform}', '-an', '-f', 'null', '-'],
                           check=True, stderr=log, env=environment)
            # Allocate an independent 4:4:4 buffer before vidstab: directly feeding
            # decoder-owned 4:2:0 reference frames caused intermittent corruption.
            filters = (trim + f',format=yuv444p,vidstabtransform=input={transform}:smoothing=4:optalgo=gauss:'
                       'maxshift=2:maxangle=0.0015:zoom=2:optzoom=0:crop=black:'
                       'interpol=bicubic:tripod=0,hqdn3d=0.35:0.6:0.5:0.7,'
                       'unsharp=3:3:0.12:3:3:0')
            raw = subprocess.check_output(common + ['-vf', filters, '-an', '-fps_mode',
                                                   'passthrough', '-pix_fmt', 'rgb24',
                                                   '-f', 'rawvideo', '-'],
                                          stderr=log, env=environment)
        frames = np.frombuffer(raw, np.uint8).reshape(-1, height, width, 3)
        assert len(frames) == last - first
        arrays.append(frames)
        print(f'Prepared stable source shot: {name} ({len(frames)} frames)', flush=True)
    return np.concatenate(arrays)


def render(source, config_path, output):
    root = config_path.parent
    config = json.loads(config_path.read_text())
    clips = config['clips']
    fps = config['timeline']['fps']
    count = config['timeline']['duration_frames']
    width, height = config['timeline']['width'], config['timeline']['height']
    duration = count / fps
    output.parent.mkdir(parents=True, exist_ok=True)
    assert count == 624 and fps == 24
    assert clips[0]['timeline_in_frame'] == 0 and clips[-1]['timeline_out_frame_exclusive'] == count
    assert all(a['timeline_out_frame_exclusive'] == b['timeline_in_frame'] for a,b in zip(clips,clips[1:]))
    assert not config['transitions'] and not config['overlays']
    frames = stabilized_frames(source, root, width, height)
    data = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams',
         'v:0', '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time', '-of',
         'json', str(source)]))
    pts = np.array([float(f['best_effort_timestamp_time']) for f in data['frames']])
    assert len(pts) == len(frames) == 730
    silent = root / 'clean-video-only.mp4'
    mapping = []
    with (root / 'render.log').open('w') as log:
        encoder = subprocess.Popen(['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y',
            '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s:v', f'{width}x{height}', '-r', str(fps),
            '-i', '-', '-an', '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-threads', '4',
            '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
            '-movflags', '+faststart', str(silent)], stdin=subprocess.PIPE, stderr=log)
        try:
            for clip in clips:
                a,b = clip['timeline_in_frame'],clip['timeline_out_frame_exclusive']
                si,so = clip['source_in_frame'],clip['source_out_frame_exclusive']
                for t in range(a,b):
                    target = clip['source_in_seconds'] + (t-a)/(b-a) * (
                        clip['source_out_seconds'] - clip['source_in_seconds'])
                    j = int(np.searchsorted(pts,target))
                    sf = min((max(si,min(so-1,j-1)),max(si,min(so-1,j))),key=lambda k: abs(pts[k]-target))
                    result = grade_frame(frames[sf],sf,t)
                    encoder.stdin.write(result.tobytes())
                    mapping.append({'timeline_frame':t,'source_frame':sf,'source_pts':float(pts[sf]),'clip':clip['id']})
                print(f"Rendered {clip['id']}: {b}/{count} frames",flush=True)
        finally:
            encoder.stdin.close()
        assert encoder.wait() == 0, 'Encoder failed; see render.log'
    filters=['[1:a]asplit='+str(len(clips))+''.join(f'[a{i}]' for i in range(len(clips)))]
    for i,clip in enumerate(clips):
        seconds=(clip['timeline_out_frame_exclusive']-clip['timeline_in_frame'])/fps
        samples=round(seconds*48000)
        rate=(clip['source_out_seconds']-clip['source_in_seconds'])/seconds
        filters.append(f"[a{i}]atrim=start={clip['source_in_seconds']:.6f}:end={clip['source_out_seconds']:.6f},"
            f'asetpts=PTS-STARTPTS,atempo={rate:.9f},aresample=48000,'
            f'aformat=sample_fmts=fltp:channel_layouts=stereo,apad=whole_len={samples},'
            f'atrim=end_sample={samples},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.002,'
            f'afade=t=out:st={seconds-.002:.9f}:d=0.002[p{i}]')
    filters.append(''.join(f'[p{i}]' for i in range(len(clips)))+
                   f'concat=n={len(clips)}:v=0:a=1,alimiter=limit=0.96:level=false:latency=true[outa]')
    graph=root/'audio-filter.txt'
    graph.write_text(';\n'.join(filters))
    with (root/'render.log').open('a') as log:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y','-i',str(silent),
            '-i',str(source),'-filter_complex_threads','2','-filter_complex_script',str(graph),
            '-map','0:v:0','-map','[outa]','-c:v','copy','-c:a','aac','-b:a','192k',
            '-ar','48000','-ac','2','-t',str(duration),'-movflags','+faststart','-map_metadata',
            '-1','-metadata','title=Aethers Club - Clean Natural Cinema',str(output)],
            check=True,stderr=log)
    result=probe(output)
    v=next(s for s in result['streams'] if s['codec_type']=='video')
    assert int(v['nb_frames'])==count and v['r_frame_rate']=='24/1'
    assert abs(float(result['format']['duration'])-duration)<.03
    subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
    manifest={'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
              'config':config,'probe':result,'frame_mapping':mapping,
              'applied':['natural Rec709 grade','restricted per-shot stabilization',
                         'fine monochromatic grain','mild denoise and restrained sharpening',
                         'six continuous clips, clean hard cuts','original audio retimed per clip']}
    output.with_suffix('.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(f'Finished and decoded successfully: {output} ({output.stat().st_size} bytes)',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--config',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    render(args.source,args.config,args.output)
