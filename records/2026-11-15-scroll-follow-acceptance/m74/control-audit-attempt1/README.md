# Read-only query-size harness correction

History supports pages of 1 to 200 records. The first audit and optional MCP History comparisons requested 1000 and received invalid_query. Capture prepare/toggle/stop/cancel operations themselves ran. The corrected audit uses limit 200 with offsets, and the MCP client now rejects every production error rather than ignoring optional comparison responses. This preserves the first attempt and reruns the MCP capture/control/cancel proof on its own real browser. The mixed native reference was already saved before the invalid list request.
