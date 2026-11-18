#!/usr/bin/env python3
"""Measure one fixture on one builder. Run from the private remote scratch directory."""
import argparse
import ctypes
import json
import math
import mmap
import os
from pathlib import Path
import re
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument("clip", type=Path)
parser.add_argument("output", type=Path)
parser.add_argument("--warm", type=int, default=5)
parser.add_argument("--busy-pilot", action="store_true")
parser.add_argument("--extra-open-skim", action="store_true")
parser.add_argument("--case", action="append", metavar="MODE:N",
                    help="run only specified cases when checking or recovering a run")
args = parser.parse_args()
if args.warm < 5 and not args.busy_pilot:
    parser.error("use at least five warm runs")
pagesize = os.sysconf("SC_PAGE_SIZE")
libc = ctypes.CDLL(None, use_errno=True)
clip = args.clip.resolve(strict=True)

def resident(fd):
    count = math.ceil(os.fstat(fd).st_size / pagesize)
    vector = (ctypes.c_ubyte * count)()
    with mmap.mmap(fd, 0, access=mmap.ACCESS_COPY) as mapped:
        data = ctypes.c_char.from_buffer(mapped)
        result = libc.mincore(ctypes.c_void_p(ctypes.addressof(data)),
                             ctypes.c_size_t(len(mapped)), vector)
        del data
        if result:
            raise OSError(ctypes.get_errno(), "mincore")
    return sum(value & 1 for value in vector) / count

def configure_cache(warm):
    with clip.open("rb") as source:
        if warm:
            while source.read(2**20):
                pass
        else:
            os.fsync(source.fileno())
            os.posix_fadvise(source.fileno(), 0, 0, os.POSIX_FADV_DONTNEED)
        return resident(source.fileno())

def busy_cpu():
    with open("/proc/stat") as stats:
        ticks = [int(n) for n in stats.readline().split()[1:9]]
    return sum(ticks[:3] + ticks[5:]) / os.sysconf("SC_CLK_TCK")

def preflight():
    print(subprocess.check_output(["uptime"], text=True).strip(), flush=True)
    print(Path("/proc/pressure/cpu").read_text().strip(), flush=True)
    start_cpu = busy_cpu()
    start = time.monotonic()
    time.sleep(3)
    other = (busy_cpu() - start_cpu) / (time.monotonic() - start)
    print(f"Preflight: {other:.2f} CPU cores active over 3 s", flush=True)
    if other > 0.5 and not args.busy_pilot:
        raise SystemExit("Quiet CPU preflight failed")
    return other

preflight_cores = preflight()
cases = [("A", 12), ("An", 12), ("A", 24), ("An", 24), ("B", 12), ("B", 24),
         ("D", 30), ("M", 12), ("M", 24), ("Cn", 0), ("C", 0)]
if args.extra_open_skim:
    cases.insert(7, ("Dopen", 30))
if args.case:
    chosen = set(args.case)
    cases = [(mode, count) for mode, count in cases if f"{mode}:{count}" in chosen]
    if len(cases) != len(chosen):
        parser.error("--case expects a known mode and tile count")
with args.output.open("x", buffering=1) as output:
    for mode, count in cases:
        for repetition in range(1 + args.warm):
            warm = repetition != 0
            cached = configure_cache(warm)
            if (warm and cached < .95) or (not warm and cached > .05):
                raise SystemExit(f"Cache state for {mode} {count}, run {repetition}: {cached:.1%}")
            if mode == "M":
                command = ["squashfs-root/usr/bin/putgd-record", "--motion", str(clip), str(count)]
                command = ["/usr/bin/time", "-f", "%U %S %M", *command]
            else:
                command = ["./bench", str(clip), mode, str(count), str(190731 + repetition)]
            before_cpu = busy_cpu()
            start_time = time.monotonic()
            run = subprocess.run(command, text=True, capture_output=True)
            wall = time.monotonic() - start_time
            host_busy = busy_cpu() - before_cpu
            if run.returncode:
                print(run.stdout, run.stderr, flush=True)
                raise SystemExit(f"{command} exited {run.returncode}")
            if mode != "M":
                measured = json.loads(run.stdout)
            else:
                user, system, rss = run.stderr.strip().splitlines()[-1].split()
                measured = dict(mode=mode, n=count, wall_ms=wall * 1000,
                                cpu_seconds=float(user) + float(system),
                                rss_kib=int(rss), motion=run.stdout.strip())
                if not re.search(r"compared=" + str(count - 1) + r"\b", run.stdout):
                    raise SystemExit(run.stdout)
            if mode != "M" and abs(measured["duration_us"] - 180_000_000) > 1000:
                raise SystemExit(f"Unexpected duration: {measured}")
            if mode in ("C", "Cn"):
                expected = measured["keys"] if mode == "Cn" else 10800
                if measured["frames"] != expected or measured["packets"] != 10800:
                    raise SystemExit(f"Unexpected full-pass count: {measured}")
                if measured["keys"] < 90 or measured["max_key_gap_us"] > 2_000_000 or measured["bframes"]:
                    raise SystemExit(f"Unexpected GOP structure: {measured}")
            elif mode in ("A", "An") and (measured["packets"] != count or measured["frames"] != count):
                raise SystemExit(f"More than one keyframe packet or frame per tile: {measured}")
            measured.update(cache="warm" if warm else "cold", cached=cached, repeat=repetition,
                            elapsed_ms=wall * 1000, preflight_cores=preflight_cores,
                            cpu_cores=measured["cpu_seconds"] / wall,
                            other_cores=max(0, host_busy - measured["cpu_seconds"]) / wall)
            if run.stderr and mode != "M":
                measured["stderr"] = run.stderr.strip()
            output.write(json.dumps(measured) + "\n")
            print(f"{clip.name}: {mode} {count:2d} {repetition} {measured['wall_ms']:8.1f} ms "
                  f"bench/other cores {measured['cpu_cores']:.2f}/{measured['other_cores']:.2f}", flush=True)
