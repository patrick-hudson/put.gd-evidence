#!/usr/bin/python3 -I
"""usage: matrix.py WORKDIR OUTDIR HOST ROW... where ROW = label=binary[=APPDIR]; exports WORKDIR/src.mkv with h264_vaapi/hevc_vaapi
(ENCODERS env picks a subset) through each putgd-record, then checks container parameter sets, decode warnings, PSNR vs the source and a contact sheet."""
import json, os, re, subprocess, sys, hashlib
work, out, host, rows = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
os.makedirs(out, exist_ok=True)
src = os.path.join(work, 'src.mkv')
encs = os.environ.get('ENCODERS', 'hevc_vaapi,h264_vaapi').split(',')
ffver = subprocess.run(['ffmpeg', '-hide_banner', '-version'], capture_output=True, text=True).stdout.splitlines()[0]
def run(cmd, **kw): return subprocess.run(cmd, capture_output=True, text=True, **kw)
def trace(path):
    t = run(['ffmpeg', '-hide_banner', '-i', path, '-map', '0:v', '-frames:v', '1', '-c', 'copy', '-bsf:v', 'trace_headers', '-f', 'null', '-']).stderr
    t = [re.sub(r'^\[trace_headers @ 0x[0-9a-f]+\] ', '', l) for l in t.splitlines()]
    ext, pkt, cur = [], [], None
    for l in t:
        if l == 'Extradata': cur = ext; continue
        if l.startswith('Packet:'):
            if pkt: break
            cur = pkt; continue
        if cur is not None: cur.append(l)
    def fields(lines):
        f = {}
        for l in lines:
            m = re.match(r'^\d+\s+(\S+)\s+[01]+ = (-?\d+)$', l)
            if m and m.group(1) in ('nal_unit_type', 'pic_height_in_luma_samples', 'conformance_window_flag', 'max_transform_hierarchy_depth_inter',
                                    'max_transform_hierarchy_depth_intra', 'transform_8x8_mode_flag', 'pic_init_qp_minus26', 'frame_crop_bottom_offset', 'conf_win_bottom_offset'):
                k = m.group(1)
                if k == 'nal_unit_type': f.setdefault('nal_types', []).append(int(m.group(2)))
                else: f.setdefault(k, int(m.group(2)))
        return f
    return fields(ext), fields(pkt)
report = []
for row in rows:
    label, binary, *appdir = row.split('=')
    for enc in encs:
        codec = 'h265' if enc == 'hevc_vaapi' else 'h264'
        name = f'{host}-{label}-{codec}'
        dst = os.path.join(out, name + '.mp4')
        env = dict(os.environ, PUTGD_RECORD_EXPORT_ENCODERS=enc)
        if appdir: env['APPDIR'] = appdir[0]
        p = run([binary, '--export', src, dst, '--codec', codec], env=env)
        e = {'host': host, 'build': label, 'encoder': enc, 'exportExit': p.returncode,
             'exportSummary': next((l for l in (p.stdout + p.stderr).splitlines() if l.startswith('encoder=') or 'recording_' in l), '')}
        if p.returncode == 0:
            e['bytes'] = os.path.getsize(dst); e['sha256'] = hashlib.sha256(open(dst, 'rb').read()).hexdigest()
            pr = run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_tag_string,extradata_size,width,height', '-of', 'json', dst])
            e['stream'] = json.loads(pr.stdout)['streams'][0]
            e['containerParamSets'], e['firstPacketInBand'] = trace(dst)
            d = run(['ffmpeg', '-hide_banner', '-nostats', '-v', 'warning', '-i', dst, '-f', 'null', '-'])
            e['decodeWarnings'] = d.stderr.strip().splitlines()[:5]
            ps = run(['ffmpeg', '-hide_banner', '-nostats', '-i', dst, '-i', src, '-lavfi', '[0:v]setpts=PTS-STARTPTS[a];[1:v]fps=30,setpts=PTS-STARTPTS[b];[a][b]psnr', '-f', 'null', '-']).stderr
            m = re.search(r'PSNR y:\S+ u:\S+ v:\S+ average:(\S+)', ps); e['psnrAverage'] = float(m.group(1)) if m else None
            run(['ffmpeg', '-hide_banner', '-v', 'error', '-y', '-i', dst, '-frames:v', '1', '-vf', 'select=not(mod(n\\,30)),scale=320:180,tile=7x1', '-fps_mode', 'vfr', os.path.join(out, name + '.png')])
            e['pass'] = bool(e['psnrAverage'] and e['psnrAverage'] > 35 and not e['decodeWarnings'] and e['stream'].get('extradata_size', 0) > 0)
        else:
            e['exportLog'] = (p.stdout + p.stderr)[-600:]
        report.append(e)
        print(json.dumps({k: e.get(k) for k in ('build', 'encoder', 'exportExit', 'bytes', 'psnrAverage', 'pass')}), flush=True)
json.dump({'host': host, 'decoder': ffver, 'sourceSha256': hashlib.sha256(open(src, 'rb').read()).hexdigest(), 'rows': report},
          open(os.path.join(out, f'matrix-{host}.json'), 'w'), indent=1)
