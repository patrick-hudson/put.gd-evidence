#!/bin/bash
# usage: verify.sh WORKDIR APPDIR LABEL  -- exports src.mkv with hevc_vaapi and h264_vaapi, traces, decodes, contact sheets
set -u
W=$1; AD=$2; L=$3; cd "$W"
for codec in h265 h264; do
  enc=$([ $codec = h265 ] && echo hevc_vaapi || echo h264_vaapi)
  out=$L-$codec.mp4
  APPDIR=$AD PUTGD_RECORD_EXPORT_ENCODERS=$enc $AD/usr/bin/putgd-record --export src.mkv $out --codec $codec > $L-$codec.export.log 2>&1
  echo "$out export=$? $(grep -o 'encoder=[^ ]* .*bytes=[0-9]*' $L-$codec.export.log | head -1) sha256=$(sha256sum $out | cut -c1-16)"
  ffmpeg -hide_banner -i $out -map 0:v -c copy -bsf:v trace_headers -f null - 2>&1 | sed -E 's/^\[trace_headers @ 0x[0-9a-f]+\] //' > $L-$codec.trace
  ffmpeg -hide_banner -v warning -i $out -f null - > $L-$codec.decode.log 2>&1; echo "  decode(9.0.2) exit=$? warnings=$(wc -l < $L-$codec.decode.log)"
  ffmpeg -hide_banner -v error -y -i $out -frames:v 1 -vf "select=not(mod(n\,30)),scale=320:180,tile=7x1" -fps_mode vfr sheets/$L-$codec.png
done
