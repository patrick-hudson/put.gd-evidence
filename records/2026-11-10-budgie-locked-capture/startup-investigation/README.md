# First-request deadline investigation

Initial head930 refused the first unlocked capture in fresh bc2, bc3 and bc4; later requests succeeded. bc4 traces the actual protocol: registry/sync sent05:07:01.632798, response dispatched05:07:02.538622, layer surface committed05:07:02.538891, destroyed at deadline05:07:02.682322 before configure. Thus setup used almost all of the one-second visibility deadline while the first Settings window was being rendered. The trace does not profile the compositor internals; first-window rendering is the observed concurrent condition.

Head4b7e01d2b gives setup a bounded5seconds, then restarts a separate1second frame deadline when its buffer/frame are committed. It still never reads pixels without a fresh visibility witness. A regression pauses only the private child labwc for1.2seconds during setup: old deadline fails, new passes. Real lock-surface refusal and unlocked-after-unlock remain strict. Exact-head native cold-start acceptance follows when its CI package is available.

bc3/bc4 archives are retained privately, matching builder and workstation SHA256; overlays stopped and guarded-retired. No physical desktop or lease used.
