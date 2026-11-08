# Final deployed installer acceptance — PASS

2026-11-08 11:19–11:24 UTC, f44 (192.168.68.70). Both tests fetched and executed the unmodified live command `curl -fsSL https://app.put.gd/install | sh -s -- --channel nightly`. No candidate file or substituted downloads used. Live script SHA256 0989850208e7689885b7a474d28fe51553f4f4d9d86a268d2f6729c00b611286 matches merged a7554a4a8d8b837f2473ed59802e8a9b1049857c, Git blob ff29bc846557e782e94204781043e369405ee930. Guest verification download has same SHA after the run.

## Clean Arch container — PASS

Official archlinux:base image identity in image.txt; new container ID in container.id/inspect. Container-only standard setup sudo/curl/keyring and complete-payload NoExtract adjustment recorded in prep.log; no host upgrade. Published installer creates key/repository config and runs pacman -Syu putgd from pkg.put.gd. Required database and package signatures; full trusted nightly fingerprint4032E28D893BAF66F4AC23D9A11D38D55536B371. `putgd-cli 26.1108.4139-nightly`; `putgd: 223 total files, 0 altered files`; repository file0644. Uninstall succeeds, package and binary absent. Container retired by exact recorded ID; logs exported first. SIGTERM grace for its sleep PID1 expired and podman terminated only this owned container.

## Fresh Omarchy / real Hyprland — PASS

Golden omarchy-hyprland-20261108, SHA256 bd74b7832c4a43f15a06f5a5b448e670a77d33ae75516b5bc5856773b69f3256; never booted or modified directly. New run7aa34550-9bbf-443c-8a8f-8e0534ad9904, QEMU2875050, KVM/2CPU/6144MiB/UEFI/virtio-vga, SSH22443/VNC5943. Guest Omarchy4.5.0/Hyprland0.56.2, native QtWayland. Unlocked active session verified by preflight and saved visuals. Socket paths50/50/31 UTF8 bytes PASS. VM tunnel unit putgd-vm-1285-o4 on free workstation5997 and backed-up/atomic wall tile registered immediately at launch, visible throughout.

NoTTY live pipeline exits1 with terminal guidance and Run omarchy update. Declined real-TTY prompt exits1; package, repo file and Include absent. Accepted real-TTY live pipeline, with actual quickshell session environment, completes native omarchy-update (snapshots, keyrings, upgrades, migrations/hooks/boot checks), then adds/syncs put.gd repository and installs putgd with pacman -S. No preparatory manual -Sy and no guard override. Exact nightly version and Qkk223zeroaltered; native production GUI observed on wall and saved native-startup-head0.ppm; capabilities and diagnostics succeeded. Clean ui.quit, socket/process disappearance and uninstall PASS, repo file remains readable by design. No capture/recording/upload or broader desktop certification claimed.

An initial harness SSH attempt preceded fresh-key bootstrap completion; no protected input sent or app action run. The exact own waiting SSH process was stopped, first failure logs retained, and checks rerun after launch preflight completed. No application/installer failure in completed checks. Masked sudo input read privately; no private key or login input in this record.

## Retirement and scope

Host evidence exported and all manifest hashes verified before guarded retirement. Manifest ebc088f50a709bc4bc440052a040f4b64ced4a6564277cf4b9e7577e17bd8ac3; disk removal completed11:23:32 UTC. Owned PID/disk/container absent, ports22443/5943 free. Only owned wall tile removed/tunnel stopped, own preview tab closed. Immutable golden, all other desktops/workers and Patrick's processes preserved.

Release v26.1108.4139-nightly, application source0eaff434d3530d3e09dc1663751eee960b7afa46. Earlier pacman lab/live publication plus apt/dnf checks remain valid in the parent record; all previously failed/candidate attempts preserved. Stable key/signing never touched; next stable promotion uses workstation sign_stable.py. All #1285 requested rollout/install/startup/cleanup checks now passed; issue closure follows publication of this pinned evidence.
