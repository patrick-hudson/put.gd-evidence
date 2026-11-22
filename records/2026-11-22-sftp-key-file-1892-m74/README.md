# SFTP key file acceptance on m74

Linux Mint 22.3, Cinnamon 6.6.9 on X11. The isolated resident matched candidate commit `9a9b36ab1308264e600b5328953771c61cc5a71b` and tree `78ae5860155e44d395cbd9ecf4fa263c054bf23d`. CI artifact `putgd_26.1122.6507~dev+g9a9b36ab1308_amd64.deb` matched SHA-256 `31e33491bf8c1fe314bebda444240f46cb4264c5b336045a672f869879fb5c87` on the builder. [Candidate CI](https://github.com/patrick-hudson/put.gd-desktop/actions/runs/45053457893)

`ssh-add -l` found no agent with `SSH_AUTH_SOCK` unset. The session socket was 40 UTF-8 bytes and the longest SFTP askpass socket path was 41 bytes. The selected key was a synthetic lab fixture in a private directory outside `~/.ssh`. [Resident diagnostics](build.json)

| Row | Result | Observation |
| --- | --- | --- |
| K1 | PASS | One Sign-in section held SSH key, Password, Key passphrase, storage choice, Store and Test. [Server and links](screenshots/K1.png) · [Sign-in](screenshots/K2Result.png) |
| K2 | PASS | A physical Choose click opened the portal chooser in `~/.ssh`. Picking `deploy.pub` set the private path and the Server line ended in `with key deploy`. [Chooser](screenshots/K2Chooser.png) · [Selected key](screenshots/K2Result.png) |
| K3 | PASS | The trust box matched the lab ED25519 fingerprint. The status read “Compare it above”. The link test passed, Firefox opened the synthetic PNG, and exact History deletion made its URL return 404. [Trust](screenshots/K3Trust.png) · [Test](screenshots/K3Test.png) · [Firefox](screenshots/K3BrowserFinal.png) · [History](screenshots/K3HistoryDeleted.png) |
| K4 | PASS | Mode 0644 showed the `chmod 600` message and Test refused sign-in. Mode 0600 passed the retest. [Field](screenshots/K4Permissions.png) · [Rejected test](screenshots/K4TestRejected.png) · [Receipt](checks.json) |
| K5 | PASS | Saved the encrypted key’s passphrase in the real desktop keychain. Test passed before and after restart with the default startup unlock preference. The typed field was empty in these frames. [Before restart](screenshots/K5BeforeRestart.png) · [After restart](screenshots/K5AfterRestart.png) |
| K6 | PASS | A second destination used the encrypted key’s session-only passphrase. Test passed before restart and reported that `locked` needs its passphrase after restart. [Before restart](screenshots/K6BeforeRestart.png) · [After restart](screenshots/K6AfterRestart.png) |
| K7 | PASS | The candidate’s official MCP helper used the production CLI to resolve `.pub`, report a missing path, clear to null, and open and cancel `sftpKey`. [Missing key](screenshots/K7Missing.png) · [MCP receipts](mcp.json) |
| K8 | PASS | The three PR pictures use one set of Debian frames. The other desktop records retain their own frames. |

## Test notes

The initial private CA override did not reach Qt’s TLS check. The system trust-store import resolved it. The failed probe’s URL returned 404. The MCP chooser frame was taken while the portal was opening. The MCP reply and the physical Choose frame cover that backend.

K5 used the product default for unlocking saved credentials at startup. On the first Debian, Kubuntu, and Mint attempt, the reused private template had disabled that preference. Those attempts required a passphrase after restart. Restoring the default gave a passing restart without retyping.

## Restoration

Reinstalled the exact original DEB `26.1122.6373~dev+gaa202c7a634c`. Removed the test keychain entry, Firefox profile and CA, private put.gd profile, and key fixtures. The exact test upload returned 404 after deletion. The builder cleanup check passed and released the desktop lease. [Restoration details](restoration.txt) · [Check receipts](checks.json)
