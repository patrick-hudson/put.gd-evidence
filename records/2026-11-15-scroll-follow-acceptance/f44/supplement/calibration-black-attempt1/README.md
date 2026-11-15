# Partial first RFB frame

This probe stopped before scroll.prepare. The black image was later diagnosed as an initial queued RFB cursor-damage update (only3nonzero bytes); subsequent complete frames showed the actual desktop. ScreenSaver=false, LockedHint=no, PowerSaveMode=0. The documented mirror service was restarted once during diagnosis, without changing its configuration. The collector now waits for a complete subsequent update. An owned setup window and GNOME focus prevention were also diagnosed before the corrected probe. No product capture was started by these calibration attempts.
