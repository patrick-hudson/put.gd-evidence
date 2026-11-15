# Initial focused keyboard attempt

Content focus was true before and after prepare, but the first End did not move the page; the operation was canceled by the harness finally block. A separate pre-capture probe with a ready acknowledgement and two-second device settling records a native End event and movement to page bottom, and Home back to top. The corrected recovery recipe waits for readiness and preflights End/Home before prepare, rather than assuming a newly created keyboard has reached the compositor.

Subsequent preflighted before/during/after comparison reproduced the failure only during capture; keyboard readiness did not explain that capture-active suppression. See keyboard-candidate/ for the validated native input probe.
