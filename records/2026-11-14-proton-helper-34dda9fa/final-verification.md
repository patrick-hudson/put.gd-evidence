# Final integration verification

The code PR head is `20ad0f11961070624a88b2dab39fda263f91d973`, based on nightly `47b67a21313d2660fd42059fa25a87ae9d432418`. The helper source files in the final provisioning manifest match the local committed sources byte for byte; catalog hash and helper hash remain unchanged.

After merging the other worker's signal fix (#1499), the required complete source checks were run again on d69. All five contract groups passed (release57 suites, proton2 suites, lab24 suites, observer18 tests, evidence replay). The complete required surface command passed **436/436 in28.59seconds**. This supersedes the earlier432/4 result as the final integration check; the earlier exact command, Python3.13.5, contemporaneous load0.54/0.24/0.16 and full traceback are retained, and no W7 product/test fix was made.

The tested desktop packages remain the authorized CI43530643130/ff636bba2 cohort with helper34dda9fa. No desktop acceptance of later application-only integration changes is claimed. All helper1399 gates passed; the three catalog flags are restored and openGates is empty. The final provision/audit binds that catalog and reproduces the identical helper.

All five final QEMU checks returned0 in separate calls at01:56UTC; no W7 VM was launched. All desktop/Proton leases were released by01:50:01UTC. The final notification cleanup closed81 old exact matches and verified0 remaining, leaving every other notice alone. One unmaterialized record's age is conservatively bounded by the same daemon's monotonic id allocation and a later timestamped id; this is explicitly recorded rather than inventing a timestamp.

The on-screen notice was from11:23UTC; the full materialized queue starts11:09 and ends18:10 onNov13. These times are consistent with the coordinator-named recognition/hotkey campaigns. Attribution to a particular harness or parent cannot be established: PID726275 is dead and journalctl returned no records for it.
