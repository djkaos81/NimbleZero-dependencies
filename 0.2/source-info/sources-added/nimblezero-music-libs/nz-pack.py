#!/usr/bin/env python3
"""Make one package of a NimbleZero package set from a staged directory, the way
make-packages.py of the set does it (same control fields, same NZ-Digest), for libraries
built outside the set's Buildroot build.

nz-pack.py --name nz-lib-libgme --version 0.2.1 --title libgme \
    --description "..." --contents "game-music-emu 0.6.5" --provides "libgme0 (= 0.6.5)" \
    [--depends "nz-lib-x (>= 0.2.1)"] --root STAGE FILE... --out DIR
FILE: paths under STAGE (e.g. usr/lib/libgme.so.0.6.5); symlinks are kept.
Prints the Packages stanza."""
import argparse, hashlib, io, lzma, os, stat, sys, tarfile, time

ap = argparse.ArgumentParser()
for a in ("name", "version", "title", "description", "contents", "root", "out"): ap.add_argument("--" + a, required=True)
ap.add_argument("--provides", default=""); ap.add_argument("--depends", default=""); ap.add_argument("--section", default="libs")
ap.add_argument("files", nargs="+")
o = ap.parse_args()
T = o.root; files = sorted(o.files)
dep_names = [d.split()[0] for d in o.depends.split(",") if d.strip()]
prov = [p.strip() for p in o.provides.split(",") if p.strip()]

meta = "\n".join([o.name, "depends " + " ".join(dep_names), "provides " + " ".join(prov), "conflicts ",
                  "section " + o.section, "title " + o.title, "contents " + o.contents, "description " + o.description])
h = hashlib.sha256(meta.encode())
for rel in files:
    fp = os.path.join(T, rel); st = os.lstat(fp)
    h.update(f"{rel}\0{stat.S_IMODE(st.st_mode):o}\0".encode())
    if stat.S_ISLNK(st.st_mode): h.update(b"L" + os.readlink(fp).encode())
    else: h.update(hashlib.sha256(open(fp, "rb").read()).digest())
dg = h.hexdigest()

def reset(ti): ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"; return ti
def ar_member(name, data):
    hd = f"{name:<16}{int(time.time()):<12}{0:<6}{0:<6}{'100644':<8}{len(data):<10}`\n".encode()
    return hd + data + (b"\n" if len(data) % 2 else b"")
def tar_xz(add):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as t: add(t)
    return lzma.compress(raw.getvalue(), preset=6)
def add_data(t):
    dirs = set()
    for rel in files:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            d = "/".join(parts[:i])
            if d not in dirs:
                dirs.add(d); ti = tarfile.TarInfo("./" + d); ti.type = tarfile.DIRTYPE; ti.mode = 0o755
                ti.mtime = int(os.lstat(os.path.join(T, d)).st_mtime); t.addfile(reset(ti))
        t.add(os.path.join(T, rel), arcname="./" + rel, recursive=False, filter=reset)
size = sum(os.lstat(os.path.join(T, f)).st_size for f in files)
ctl = [f"Package: {o.name}", f"Version: {o.version}", "Architecture: arm64",
       "Maintainer: NimbleZero <https://github.com/djkaos81/NimbleZero>",
       f"Installed-Size: {max(1, size // 1024)}", f"Section: {o.section}", "Priority: optional"]
if o.depends: ctl.append("Depends: " + o.depends)
if prov: ctl.append("Provides: " + ", ".join(prov))
ctl += [f"NZ-Title: {o.title}", f"NZ-Contents: {o.contents}", f"NZ-Digest: {dg}", f"Description: {o.description}"]
control = "\n".join(ctl) + "\n"
def add_ctl(t):
    b = control.encode(); ti = tarfile.TarInfo("./control"); ti.size = len(b); ti.mode = 0o644
    ti.mtime = int(time.time()); t.addfile(reset(ti), io.BytesIO(b))
blob = b"!<arch>\n" + ar_member("debian-binary", b"2.0\n") + ar_member("control.tar.xz", tar_xz(add_ctl)) + ar_member("data.tar.xz", tar_xz(add_data))
fn = f"{o.name}_{o.version}_arm64.deb"
os.makedirs(o.out, exist_ok=True)
open(os.path.join(o.out, fn), "wb").write(blob)
sys.stdout.write(control + f"Filename: {fn}\nSize: {len(blob)}\nSHA256: {hashlib.sha256(blob).hexdigest()}\n")
