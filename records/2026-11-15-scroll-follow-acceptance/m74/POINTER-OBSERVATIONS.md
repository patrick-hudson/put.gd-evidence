# Relative-pointer observations requiring review

Only the authoritative first20 trials are included. Raw post-hand events include the permitted one put-back; see the narrative for full-gate verdict and clock precision. k72 has four ordinary events within1ms of the first motion whose ordering is uncertain; its late put-backs and the missed random10 click are definite. Baseline comparisons and native-position calibration are in README.md.

## random-7

Operation `c0be1eca-9040-4718-bc1d-e4198d50ef44`. First click stopped: **False**. Target [737, 142]; actual native cursor before click [705, 46]. Pause 40.77494788169861ms; clock resolution 1ms. Terminal done/done. Raw events after first hand: 3; put-backs 0. Motion source is the real relative uinput mouse; absolute VNC is not used by the pointer gate.

[trial-random-7.log](trial-random-7.log)

[click-miss-random-7.png](click-miss-random-7.png)

```text
2026-11-14T20:58:26.349 scroll inject: t=414590 pointer 48,48 sent
2026-11-14T20:58:26.351 scroll inject: t=414592 wheel 2 sent
2026-11-14T20:58:26.382 scroll inject: t=414623 pointer 16,-48 sent
```

