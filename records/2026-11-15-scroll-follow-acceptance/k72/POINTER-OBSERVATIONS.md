# Relative-pointer observations requiring review

Only the authoritative first20 trials are included. Raw post-hand events include the permitted one put-back; see the narrative for full-gate verdict and clock precision. k72 has four ordinary events within1ms of the first motion whose ordering is uncertain; its late put-backs and the missed random10 click are definite. Baseline comparisons and native-position calibration are in README.md.

## fixed-6

Operation `acba4b70-6345-4a75-9c10-b0dc3cf594f1`. First click stopped: **True**. Target [737, 164]; actual native cursor before click [737, 164]. Pause 1.6257269382476807ms; clock resolution 1ms. Terminal done/done. Raw events after first hand: 2; put-backs 1. Motion source is the real relative uinput mouse; absolute VNC is not used by the pointer gate.

[trial-fixed-6.log](trial-fixed-6.log)

```text
2026-11-15T02:44:41.099 scroll inject: t=995126 pointer 48,48 sent
2026-11-15T02:44:41.152 scroll inject: t=995179 pointer put back by 6,0 sent
```

## fixed-7

Operation `230e775f-243a-4aba-9076-7d5220b0d4a3`. First click stopped: **True**. Target [737, 164]; actual native cursor before click [737, 164]. Pause 1.8272500038146973ms; clock resolution 1ms. Terminal done/done. Raw events after first hand: 1; put-backs 0. Motion source is the real relative uinput mouse; absolute VNC is not used by the pointer gate.

[trial-fixed-7.log](trial-fixed-7.log)

[click-miss-fixed-7.png](click-miss-fixed-7.png)

```text
2026-11-15T02:44:47.936 scroll inject: t=1964 pointer 16,-26 sent
```

## random-7

Operation `3784c020-1052-431b-a504-8c25cd526b6c`. First click stopped: **True**. Target [737, 164]; actual native cursor before click [737, 164]. Pause 2.811568021774292ms; clock resolution 1ms. Terminal done/done. Raw events after first hand: 2; put-backs 1. Motion source is the real relative uinput mouse; absolute VNC is not used by the pointer gate.

[trial-random-7.log](trial-random-7.log)

```text
2026-11-15T02:46:01.168 scroll inject: t=75196 pointer 48,48 sent
2026-11-15T02:46:01.229 scroll inject: t=75257 pointer put back by 6,0 sent
```

## random-10

Operation `0e9ec0ac-627f-40de-a4a6-3a077cdf1dd3`. First click stopped: **False**. Target [737, 164]; actual native cursor before click [711, 90]. Pause 4.331687927246094ms; clock resolution 1ms. Terminal done/done. Raw events after first hand: 2; put-backs 1. Motion source is the real relative uinput mouse; absolute VNC is not used by the pointer gate.

[trial-random-10.log](trial-random-10.log)

[click-miss-random-10.png](click-miss-random-10.png)

```text
2026-11-15T02:46:25.036 scroll inject: t=99064 pointer 48,48 sent
2026-11-15T02:46:25.152 scroll inject: t=99180 pointer put back by -26,-74 sent
```

