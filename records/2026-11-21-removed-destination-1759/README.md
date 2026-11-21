# Deleting files whose destination was removed (#1759, PR #1760)

Desktop acceptance of PR #1760 head `e14505ed17f8ae18768c1a32a9dc50bde91bb693`, using the
AppImage that CI run 44867739998 (`ci.yml` dispatched on `candidate/removed-destination-1759`
at that commit, tree `9bbe1006c10dc08a81be2f322f4cf9588beaee1b`) built:
`putgd-26.1121.5976-dev+ge14505ed17f8-x86_64.AppImage`. Every window's footer shows that version.

Host: k72, Kubuntu 26.04 Plasma Wayland, under the desktop lock (session `removed-1759-b`,
released clean; an earlier rehearsal on candidate `a0370d2` used session `removed-1759-a` and
found the two UI problems fixed in `e14505e`). The resident ran from the AppImage with private
XDG folders on the real session. The destination was an S3 destination ("Work S3", bucket
`putgd-shots`, keychain credentials) on the repository's offline S3 fixture
(`tests/fixtures/s3_server.py`, synthetic keys only). Pictures are annotated with put.gd's own
editor (`editor.open`/`apply`/`saveCopy`).

Steps and results:

1. Uploaded `team-standup.png` and `invoice-draft.png` separately to Work S3.
2. Settings, Destinations, Work S3, More, Remove destination: the confirmation says
   "2 History items were uploaded to it; their files stay there" (`1-remove-destination-count.png`).
   Removed it.
3. History marks both rows "Destination removed" (`2-history-destination-removed.png`).
4. invoice-draft's row menu offers "Remove from History only…"; its dialog says the file stays
   where it was uploaded and offers Remove from History only (`3-remove-from-history-only.png`).
   After it, only the History record is gone; a HEAD on `putgd-shots/invoice-draft.png` still
   answered 200 (`4-removed-from-history.png`).
5. Added a destination back for the same endpoint and bucket under another ID
   (`work-s3-again`, "Work S3 (added back)", own keychain entry) over the session. The marker
   left team-standup's row; its menu offered Delete from destination. Deleting it ran through
   `work-s3-again` (`delete.inspect`: item `removed`, `deletingProfileId` `work-s3-again`),
   the row reads "Deleted from destination", and a HEAD on `putgd-shots/team-standup.png`
   answered 404 (`5-deleted-through-added-back.png`).

Notes: "Changes not saved" in the last picture's footer is the open Settings window's designed
conflict state: the destination was added back over the session while that window held the
routing edits its own removal made. A commit after this head fixes the one-item wording of the
removal confirmation ("delete them" for one file). The lab keychain items were deleted afterwards.
