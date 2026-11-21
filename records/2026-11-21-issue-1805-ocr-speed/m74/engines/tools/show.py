import json, sys
d = json.load(sys.stdin)
for k in ('all', 'screens_1080p', 'screens_m74_125', 'gnome_4k', 'regions'):
    print(k, d[k])
print('classes cer_med/pooled/vs_today_med:', {k: (v['cer_med'], v['cer_pooled'], v.get('cer_vs_today_med')) for k, v in d['classes'].items()})
print('worst', d['worst'])
