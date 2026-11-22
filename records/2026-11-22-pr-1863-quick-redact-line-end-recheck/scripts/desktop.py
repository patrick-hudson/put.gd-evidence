#!/usr/bin/env python3
"""Drive installed put.gd against real windows on a locked physical builder."""
import argparse
import ctypes
import html
import json
import os
from pathlib import Path
import signal
import subprocess as sp
import time


root = Path("/tmp/qr1863")
uid = os.getuid()
runtime = Path(f"/run/user/{uid}")
token = "gh" + "p_" + "aB3dE5fG7hJ9kL1mN3pQ" + "5rS7tU9vW1xY3zA5"
aws = "AK" + "IA" + "IOSFODNN7EXAMPLE"
hex_body = "839adbf087acd6713a926bf311dab5c9" + "a470abc89f071196b743e1021427fedc"
jwt = ".".join([
    "ey" + "JhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
    "ey" + "JzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ",
    "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
])
header, _, signature = jwt.split(".")
payload = "ey" + "JzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkV4YW1wbGUifQ"
long_jwt = ".".join([header, payload * 13, signature])
dot_payload = "ey" + "JzdWIiOiJleGFtcGxlLXVzZXItOTk5OSJ9"
dot_jwt = ".".join([header, dot_payload, signature[:36]])
cases = {
    "1": ("editor", [f"Bearer {token}", "4539 1488 0343 6467", "4111 1111 1111 1111", f'SIGNING_HEX = "{hex_body}"']),
    "2": ("editor", [f"Bearer {token}", "ops-alerts@example.com"]),
    "3": ("editor", [f"Bearer {token}", aws]),
    "4": ("terminal", [f"Bearer {token}", "add more tests later"]),
    "5-jwt": ("editor", [jwt]),
    "5-jwt-labeled": ("editor", ["token: " + jwt.replace(
        "IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ", "IkV4YW1wbGUifQ")]),
    "5-hex-three": ("editor", [f'SIGNING_HEX = "{hex_body}"']),
    "5-hex": ("editor", [f'SIGNING_HEX = "{hex_body}"']),
    "a-dot-jwt": ("wrapped-browser", [dot_jwt]),
    "b-long-jwt": ("editor", ["  " + long_jwt]),
    "c-loose-hex": ("wrapped-browser", [f'SIGNING_HEX = "{hex_body}"']),
    "6": ("browser", [f"Bearer {token}", "5555 5555 5555 4444", "4539 1488 0343 6467"]),
}
assert len(token) == 40 and len(hex_body) == 64
assert 690 <= len(long_jwt) <= 760 and len(header) + 1 == len(dot_payload) + 1 == 37

def dump(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")

def environment(host):
    shell = "cinnamon" if host == "m74" else "plasmashell"
    pid = sp.check_output(["pgrep", "-nx", shell], text=True).strip()
    session = dict(item.split("=", 1) for item in
                   Path(f"/proc/{pid}/environ").read_bytes().decode().split("\0") if "=" in item)
    env = os.environ.copy()
    for name in ("DISPLAY", "XAUTHORITY", "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "WAYLAND_DISPLAY"):
        env.pop(name, None)
        if name in session:
            env[name] = session[name]
    env.update(XDG_RUNTIME_DIR=str(runtime), DBUS_SESSION_BUS_ADDRESS=f"unix:path={runtime}/bus")
    expected = "x11" if host == "m74" else "wayland"
    assert env["XDG_SESSION_TYPE"] == expected, env["XDG_SESSION_TYPE"]
    if host == "k72":
        env.setdefault("WAYLAND_DISPLAY", "wayland-0")
    return env

def private(env, path):
    path.mkdir(mode=0o700, exist_ok=True)
    result = env.copy()
    for kind in ("CONFIG", "CACHE", "STATE", "DATA"):
        target = path / kind.lower()
        target.mkdir(mode=0o700, exist_ok=True)
        result[f"XDG_{kind}_HOME"] = str(target)
    return result

def cli(env, method, params=None, allow_error=False):
    p = sp.run(["/usr/bin/putgd-cli", method, json.dumps(params or {})],
               env=env, capture_output=True, text=True, timeout=100)
    reply = json.loads(p.stdout)
    if not allow_error and not reply["ok"]:
        raise RuntimeError(f"{method}: {reply['error']}")
    return reply

def wait_ready(env, method, params=None, ready=lambda reply: reply["ok"]):
    for _ in range(80):
        reply = cli(env, method, params, allow_error=True)
        if ready(reply):
            return reply
        time.sleep(0.25)
    raise RuntimeError(f"{method}: {reply}")

def stop(p):
    if p and p.poll() is None:
        p.terminate()
        try:
            p.wait(timeout=12)
        except sp.TimeoutExpired:
            p.kill()
            p.wait(timeout=10)

def arrange_kde(env, pid, width, title):
    script = root / "arrange.js"
    script.write_text(f"""
for (const w of workspace.windowList()) {{
    if (w.pid !== {pid} && !String(w.caption).includes({json.dumps(title)})) continue;
    w.setMaximize(false, false);
    w.frameGeometry = {{x:65, y:65, width:{width}, height:450}};
    workspace.activeWindow = w;
}}
""")
    args = ["qdbus6", "org.kde.KWin"]
    name = "qr1863-" + str(pid)
    number = sp.check_output(args + ["/Scripting", "org.kde.kwin.Scripting.loadScript",
                                   str(script), name], env=env, text=True).strip()
    try:
        sp.run(args + [f"/Scripting/Script{number}", "org.kde.kwin.Script.run"],
               env=env, check=True)
    finally:
        sp.run(args + ["/Scripting", "org.kde.kwin.Scripting.unloadScript", name],
               env=env, check=True)

class AdoptedKate:
    def __init__(self, pid):
        self.pid = pid

    def poll(self):
        if hasattr(self, "returncode"):
            return self.returncode
        done, status = os.waitpid(self.pid, os.WNOHANG)
        if done:
            self.returncode = os.waitstatus_to_exitcode(status)
            return self.returncode
        return None

    def wait(self, timeout):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            status = self.poll()
            if status is not None:
                return status
            time.sleep(0.05)
        raise sp.TimeoutExpired("kate", timeout)

    def terminate(self):
        os.kill(self.pid, signal.SIGTERM)

    def kill(self):
        os.kill(self.pid, signal.SIGKILL)

def adopt_kate(source):
    pid = os.getpid()
    children = Path(f"/proc/{pid}/task/{pid}/children")
    for _ in range(40):
        for child in children.read_text().split():
            process = Path("/proc") / child
            try:
                argv = (process / "cmdline").read_bytes().split(b"\0")
                exe = (process / "exe").resolve(strict=True)
            except FileNotFoundError:
                continue
            if exe == Path("/usr/bin/kate") and os.fsencode(source) in argv:
                return AdoptedKate(int(child))
        time.sleep(0.1)
    raise RuntimeError("could not identify the Kate process started for this fixture")

def window(host, case, env, log):
    kind, lines = cases[case]
    label = "qr1863-case-" + case
    source = root / (label + ".txt")
    editor_height = 810 if case == "b-long-jwt" else 405
    source.write_text("\n".join(lines) + "\n")
    if kind == "editor":
        settings_env = private(env, root / "editor")
        width = {"5-jwt": 1058, "5-jwt-labeled": 839, "5-hex": 1227, "5-hex-three": 1244}.get(case, 1530)
        if host == "k72" and case in ("5-hex", "5-hex-three"):
            width = 1060 if case == "5-hex" else 1073
        if host == "m74":
            settings_env["GSETTINGS_BACKEND"] = "keyfile"
            for key, value in {
                "use-default-font": "false", "editor-font": "Monospace 20",
                "wrap-mode": "char", "auto-indent": "false",
            }.items():
                sp.run(["gsettings", "set", "org.x.editor.preferences.editor", key, value],
                       env=settings_env, check=True)
            argv = ["xed", "-s", "-g", f"{width}x{editor_height}+65+65", str(source)]
        else:
            (Path(settings_env["XDG_CONFIG_HOME"]) / "katerc").write_text(
                "[KTextEditor Document]\nDynamic Word Wrap=true\n"
                "[KTextEditor View]\nDynamic Word Wrap=true\nDynamic Word Wrap Align Indent=0\n"
                "[KTextEditor Renderer]\nFont=DejaVu Sans Mono,20,-1,5,400,0,0,0,0,0,0,0,0,0,0,1\n")
            settings_env["QT_QPA_PLATFORM"] = "wayland"
            settings_env["QT_SCALE_FACTOR"] = "1.7"
            argv = ["kate", "-n", str(source)]
    elif kind == "terminal":
        settings_env = env
        argv = ["xterm", "-T", label, "-geometry", "72x12+65+65", "-fa", "DejaVu Sans Mono",
                "-fs", "23", "-fg", "black", "-bg", "white", "-e",
                "sh", "-c", 'cat "$1"; exec sleep 300', "fixture", str(source)]
    else:
        settings_env = env.copy()
        if host == "k72":
            settings_env["MOZ_ENABLE_WAYLAND"] = "1"
        base = root if host == "m74" else Path.home() / "snap/firefox/common"
        profile = base / "qr1863-browser"
        profile.mkdir(mode=0o700, exist_ok=True)
        (profile / "user.js").write_text(
            'user_pref("browser.aboutwelcome.enabled", false);\n'
            'user_pref("browser.shell.checkDefaultBrowser", false);\n'
            'user_pref("browser.startup.homepage_override.mstone", "ignore");\n')
        page = base / "qr1863-layout.html"
        if kind == "wrapped-browser":
            columns = 38 if case == "a-dot-jwt" else 76.02
            line_height = "1.25" if case == "a-dot-jwt" else "2.2"
            content = html.escape(lines[0])
            if case == "a-dot-jwt":
                parts = dot_jwt.split(".")
                parts[0] += "."
                parts[1] += "."
                content = "<wbr>".join(
                    f'<span style="white-space:nowrap">{html.escape(part)}</span>' for part in parts)
            body = (f'<pre style="left:64px;top:80px;white-space:pre-wrap;word-break:break-all;'
                    f'width:{columns}ch;line-height:{line_height}">{content}</pre>')
        else:
            body = "".join(f'<pre style="left:{x}px;top:{y}px">{html.escape(line)}</pre>'
                           for line, (x, y) in zip(lines, [(64, 80), (600, 130), (64, 475)]))
        page.write_text("<!doctype html><meta charset=utf-8><title>" + label +
                        "</title><style>body{background:white;color:black}pre{position:absolute;"
                        "margin:0;font:32px/40px 'DejaVu Sans Mono'}</style>" +
                        body)
        argv = ["firefox", "--no-remote", "--profile", str(profile), "--kiosk", page.as_uri()]
    process = sp.Popen(argv, env=settings_env, stdin=sp.DEVNULL, stdout=log, stderr=log)
    try:
        if host == "m74":
            found = None
            for _ in range(60):
                match = sp.run(["xdotool", "search", "--onlyvisible", "--name", label],
                               env=env, capture_output=True, text=True)
                if match.returncode == 0:
                    found = match.stdout.splitlines()[-1]
                    break
                time.sleep(0.25)
            if found is None:
                raise RuntimeError(f"fixture {label} never appeared")
            if kind == "editor":
                sp.run(["xdotool", "windowsize", found, str(width), str(editor_height),
                        "windowmove", found, "65", "65"], env=env, check=True)
            sp.run(["xdotool", "windowactivate", "--sync", found], env=env, check=True)
        else:
            time.sleep(10 if kind == "browser" else 1.5)
        if host == "k72" and kind == "editor" and process.poll() == 0:
            process = adopt_kate(source)
        if host == "k72" and kind != "browser":
            arrange_kde(env, process.pid, width if kind == "editor" else 1200, label)
        if process.poll() is not None:
            raise RuntimeError(f"{argv[0]} exited with {process.returncode}")
        time.sleep(0.6)
        return process
    except BaseException:
        stop(process)
        raise

def capture(env, folder, crop=None):
    operation = cli(env, "editor.open", {"source": "desktop"})
    dump(folder / "open.json", operation)
    details = operation["result"]
    target = {"id": details.get("operationId") or details["id"]}
    try:
        wait_ready(env, "editor.inspect", target)
        if crop:
            cli(env, "editor.apply", dict(target, commands=[{"op": "crop", "rect": crop}]))
        cli(env, "editor.saveCopy", dict(target, path=str(folder / "capture.png")))
        if crop is None:
            return
        cli(env, "editor.recognize", target)
        before = wait_ready(env, "editor.inspect", target, lambda r:
                            r["ok"] and r["result"]["text"]["state"] in ("completed", "failed"))
        dump(folder / "inspect-before.json", before)
        apply = cli(env, "editor.apply", dict(target, commands=[{
            "op": "redactText", "categories": ["email", "phone", "ip", "card", "key"],
        }]))
        dump(folder / "apply.json", apply)
        dump(folder / "inspect-after.json", cli(env, "editor.inspect", target))
        dump(folder / "save-copy.json", cli(env, "editor.saveCopy",
                                            dict(target, path=str(folder / "redacted.png"))))
        print(folder.name, apply["result"]["counts"], flush=True)
    finally:
        cli(env, "editor.cancel", target, allow_error=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("host", choices=["m74", "k72"])
    parser.add_argument("run")
    parser.add_argument("cases", nargs="+", choices=list(cases))
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    if args.host == "k72":
        # Kate can detach. Adopt its child so cleanup can signal the exact PID.
        if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), "PR_SET_CHILD_SUBREAPER")
    out = root / args.run
    out.mkdir(mode=0o700, exist_ok=True)
    env = environment(args.host)
    resident_env = private(env, out / "profile")
    session_path = root / ("r-" + args.run)
    session_path.mkdir(mode=0o700, exist_ok=False)
    socket = session_path.resolve() / "putgd/session.sock"
    length = len(os.fsencode(socket))
    assert length <= 107, str(socket)
    print(f"{socket}: {length} UTF-8 bytes", flush=True)
    resident_env.update(XDG_RUNTIME_DIR=str(session_path), PIPEWIRE_RUNTIME_DIR=str(runtime),
                        PULSE_SERVER=f"unix:{runtime}/pulse/native")
    if resident_env.get("WAYLAND_DISPLAY"):
        resident_env["WAYLAND_DISPLAY"] = str(runtime / env["WAYLAND_DISPLAY"])
    dump(out / "session.json", {"socketPath": str(socket), "socketBytes": length,
                               "sessionType": env["XDG_SESSION_TYPE"], "desktop": env.get("XDG_CURRENT_DESKTOP")})
    crops = {} if args.preview else json.loads((root / f"crops-{args.host}-review.json").read_text())
    with (out / "resident.log").open("w") as log:
        resident = sp.Popen(["/usr/bin/putgd", "--background"], env=resident_env,
                            stdin=sp.DEVNULL, stdout=log, stderr=log)
        try:
            for _ in range(60):
                if socket.is_socket():
                    break
                if resident.poll() is not None:
                    raise RuntimeError("resident exited")
                time.sleep(0.25)
            build = cli(resident_env, "diagnostics")["result"]["build"]
            dump(out / "build.json", build)
            assert build["gitCommit"] == "aa202c7a634c0ec4e789aea5709414bc282a225d", build
            assert build["gitTree"] == "1eee62d523786233134010ebab9aec49c1141008", build
            settings = cli(resident_env, "settings.get")["result"]["metadata"]
            cli(resident_env, "settings.patch", {
                "expectedRevision": settings.get("observedRevision") or "",
                "patch": {"archive": {"keepUploads": True, "root": str(out / "archive")},
                          "captureDefaults": {"destination": "local", "profileId": None, "publicationMode": "default"}},
            })
            for case in args.cases:
                folder = out / case
                folder.mkdir(mode=0o700)
                with (folder / "fixture.log").open("w") as fixture_log:
                    process = window(args.host, case, env, fixture_log)
                    try:
                        capture(resident_env, folder, crops.get(case))
                    finally:
                        stop(process)
                time.sleep(0.35)
        finally:
            stop(resident)

if __name__ == "__main__":
    signal.signal(signal.SIGHUP, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    main()
