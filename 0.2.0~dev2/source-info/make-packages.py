#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Cut installable .deb packages out of one finished Buildroot build.

Every file in the target directory belongs to exactly one of:
  * the base system (what the base image ships), or
  * one package (.deb) of the NimbleZero-dependencies repository.

Inputs (all from the same build):
  O/build/packages-file-list.txt   which Buildroot package installed which file
  `make show-info` JSON            Buildroot package versions, licences, dependencies
  O/target                         the finished files
  packages/groups.conf             which Buildroot packages form which .deb
  provided.map                     Debian package names each library stands for

Rules:
  * Buildroot packages reachable from a base root stay in the base, unless a group
    names them.
  * A Buildroot package named in a group goes into that group's .deb.
  * Any other package needed by exactly one .deb is folded into it; needed by several,
    it becomes its own library .deb (nz-lib-<name>).
  * Depends are computed from the ELF NEEDED entries and added to those in groups.conf.
  * A file of the base that needs a library outside the base is an error.

usage: make-packages.py O SHOW_INFO.json GROUPS.conf PROVIDED.map OSVERSION OUTDIR [--check-only]
"""
import sys, os, json, re, io, tarfile, hashlib, lzma, stat, struct, time, collections, fnmatch

def die(m): sys.exit("make-packages: " + m)

if len(sys.argv) < 7: die(__doc__)
O, INFO, GROUPS, PROVIDED, OSVER, OUT = sys.argv[1:7]
CHECK_ONLY = "--check-only" in sys.argv
T = os.path.join(O, "target")
info = json.load(open(INFO))
target_pkgs = {k for k, v in info.items() if v.get("type") == "target"}

# ---- groups.conf ---------------------------------------------------------------------
# [base]            roots = a b c
# [nz-name]         packages = a b     depends = nz-x     section = dependency|runtime
#                   title = ...        description = ...    repo = deps|apps (default deps)
#                   files = pkg:glob ...   (take only matching files of a package that
#                                           otherwise belongs elsewhere)
groups = collections.OrderedDict(); cur = None
for raw in open(GROUPS):
    line = raw.split("#", 1)[0].rstrip()
    if not line.strip(): continue
    m = re.match(r"\[(.+)\]$", line.strip())
    if m: cur = groups.setdefault(m.group(1), {}); continue
    if cur is None or "=" not in line: die("groups.conf: bad line: " + raw)
    k, v = line.split("=", 1); cur[k.strip()] = (cur.get(k.strip(), "") + " " + v.strip()).strip()
base_roots = set(groups.pop("base", {}).get("roots", "").split())
for g in list(base_roots) + [p for c in groups.values() for p in c.get("packages", "").split()]:
    if g not in target_pkgs: die(f"groups.conf names '{g}', which this build does not contain")

def deps(p):
    return [d for d in info[p].get("dependencies", []) if d in target_pkgs]
explicit = {p for c in groups.values() for p in c.get("packages", "").split()}
def closure(roots, stop=()):
    seen = set(); todo = list(roots)
    while todo:
        p = todo.pop()
        if p in seen or p in stop: continue
        seen.add(p); todo += deps(p)
    return seen

# Buildroot's dependencies include optional ones ("use it if it is in the build"), so a
# base package can point at a package that a group claims.  The group keeps it; whether
# the base really needs one of its files at run time is what the ELF check below decides.
for r in base_roots:
    if r in explicit: die(f"{r} is a base root and also in a group")
base = closure(base_roots, explicit)
owner = {}                                   # Buildroot package -> deb name
for deb, c in groups.items():
    for p in c.get("packages", "").split():
        if p in owner: die(f"{p} is in two groups")
        owner[p] = deb
# who needs the unassigned ones?
need = collections.defaultdict(set)
for deb, c in groups.items():
    for root in c.get("packages", "").split():
        for p in closure([root], explicit - {root}):
            if p not in base and p not in owner: need[p].add(deb)
auto_libs = set(); orphans = set()
for p in sorted(target_pkgs - base - set(owner)):
    users = need.get(p, set())
    if len(users) == 1: owner[p] = next(iter(users))
    elif len(users) > 1: owner[p] = "nz-lib-" + p.lower().replace("_", "-"); auto_libs.add(owner[p])
    else: orphans.add(p)                     # fine if it owns no files (virtual packages)

# ---- files ---------------------------------------------------------------------------
file_pkg = {}
for l in open(os.path.join(O, "build", "packages-file-list.txt")):
    p, f = l.rstrip("\n").split(",", 1)
    file_pkg[f[2:] if f.startswith("./") else f.lstrip("/")] = p
overrides = []                               # (brpkg, glob, deb)
for deb, c in groups.items():
    for spec in c.get("files", "").split():
        p, g = spec.split(":", 1); overrides.append((p, g, deb))
deb_files = collections.defaultdict(list); base_files = []; unowned = 0; orphan_files = collections.Counter()
for root, dirs, files in os.walk(T):
    for n in files + [d for d in dirs if os.path.islink(os.path.join(root, d))]:
        rel = os.path.relpath(os.path.join(root, n), T)
        p = file_pkg.get(rel)
        dst = None
        if p in orphans: orphan_files[p] += 1; continue
        if p:
            for op, g, deb in overrides:
                if op == p and fnmatch.fnmatch("/" + rel, g): dst = deb; break
            if dst is None: dst = owner.get(p)
        else: unowned += 1
        (deb_files[dst] if dst else base_files).append(rel)

if orphan_files: die('in the build, but neither the base nor any group needs them: ' + ', '.join(f'{p} ({n} files)' for p, n in sorted(orphan_files.items())))

# ---- ELF dependencies ----------------------------------------------------------------
def needed(path):
    try:
        with open(path, "rb") as f:
            h = f.read(64)
            if h[:4] != b"\x7fELF" or h[4] != 2: return None
            shoff = struct.unpack_from("<Q", h, 0x28)[0]; shentsize, shnum = struct.unpack_from("<HH", h, 0x3A)
            f.seek(shoff); sh = f.read(shentsize * shnum); out = []
            for i in range(shnum):
                typ = struct.unpack_from("<I", sh, i * shentsize + 4)[0]
                if typ != 6: continue        # SHT_DYNAMIC
                off, size = struct.unpack_from("<QQ", sh, i * shentsize + 0x18)
                link = struct.unpack_from("<I", sh, i * shentsize + 0x28)[0]
                stroff = struct.unpack_from("<Q", sh, link * shentsize + 0x18)[0]
                f.seek(off); dyn = f.read(size)
                for j in range(0, len(dyn), 16):
                    tag, val = struct.unpack_from("<QQ", dyn, j)
                    if tag == 1:
                        f.seek(stroff + val); out.append(f.read(256).split(b"\0")[0].decode())
            return out
    except (OSError, struct.error): return None

where = {}                                   # soname -> None (base) | deb
def reg(files, tag):
    for rel in files:
        b = os.path.basename(rel)
        if ".so" in b and "/python" not in rel: where.setdefault(b, tag)
reg(base_files, None)
for deb, fl in deb_files.items(): reg(fl, deb)
errors = []; auto_dep = collections.defaultdict(set); why = {}
def scan(files, me):
    for rel in files:
        fp = os.path.join(T, rel)
        if os.path.islink(fp): continue
        for so in needed(fp) or []:
            if so not in where:
                errors.append(f"{rel} needs {so}, which no package provides"); continue
            w = where[so]
            if w is None or w == me: continue
            if me is None: errors.append(f"base file {rel} needs {so} from package {w}")
            else: auto_dep[me].add(w); why.setdefault((me, w), f"{rel} needs {so}")
scan(base_files, None)
for deb, fl in deb_files.items(): scan(fl, deb)

# ---- Debian names (Provides) ---------------------------------------------------------
provides = collections.defaultdict(list)
fileset = {deb: set(fl) for deb, fl in deb_files.items()}
for l in open(PROVIDED):
    l = l.split("#", 1)[0].strip()
    if not l: continue
    names, proof, src = l.split("|")
    rel = proof.lstrip("/")
    for deb, fl in deb_files.items():
        if rel in fileset[deb] or "usr/" + rel in fileset[deb] or any(f.startswith(rel + "/") for f in fl):
            ver = info.get(src, {}).get("version", OSVER) if not src.startswith("@") else OSVER
            provides[deb] += [f"{n} (= {ver})" for n in names.split(",")]

# ---- report --------------------------------------------------------------------------
def size(files): return sum(os.lstat(os.path.join(T, f)).st_size for f in files)
rep = {"os_version": OSVER, "base": {"files": len(base_files), "bytes": size(base_files),
       "buildroot_packages": sorted(base), "files_without_package": unowned}, "packages": {}}
for deb in sorted(deb_files):
    c = groups.get(deb, {})
    dep = sorted(set(c.get("depends", "").split()) | auto_dep[deb])
    rep["packages"][deb] = {"files": len(deb_files[deb]), "bytes": size(deb_files[deb]), "depends": dep,
        "buildroot_packages": sorted(p for p, d in owner.items() if d == deb),
        "provides": provides[deb], "library": deb in auto_libs}
rep["errors"] = errors
os.makedirs(OUT, exist_ok=True)
json.dump(rep, open(os.path.join(OUT, "packages-report.json"), "w"), indent=1)
print(f"base: {len(base_files)} files, {size(base_files)/1e6:.1f} MB ({unowned} files belong to no Buildroot package)")
for deb, r in rep["packages"].items():
    print(f"{r['bytes']/1e6:7.1f} MB  {deb:28s} {len(r['buildroot_packages']):2d} pkgs  depends: {' '.join(r['depends']) or '-'}")
if "--why" in sys.argv:
    for (a, b), r in sorted(why.items()): print(f"WHY {a} -> {b}: {r}")
for e in errors[:40]: print("ERROR:", e)
if errors: die(f"{len(errors)} dependency error(s)")
if CHECK_ONLY: sys.exit(0)

# ---- write .deb files and the index --------------------------------------------------
def ar_member(name, data):
    h = f"{name:<16}{int(time.time()):<12}{0:<6}{0:<6}{'100644':<8}{len(data):<10}`\n".encode()
    return h + data + (b"\n" if len(data) % 2 else b"")
def tar_xz(add):
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.GNU_FORMAT) as t: add(t)
    return lzma.compress(raw.getvalue(), preset=6)
def reset(ti):
    ti.uid = ti.gid = 0; ti.uname = ti.gname = "root"; return ti

index = collections.defaultdict(list)       # repository (deps | apps) -> index entries
for deb, r in rep["packages"].items():
    c = groups.get(deb, {}); files = sorted(deb_files[deb])
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
    brp = r["buildroot_packages"]
    desc = c.get("description") or ("Library package built from " + ", ".join(brp))
    contents = ", ".join(f"{p} {info[p].get('version','')}".strip() for p in brp)
    ctl = [f"Package: {deb}", f"Version: {OSVER}", "Architecture: arm64",
           "Maintainer: NimbleZero <https://github.com/djkaos81/NimbleZero>",
           f"Installed-Size: {max(1, r['bytes'] // 1024)}",
           f"Section: {'libs' if r['library'] else c.get('section', 'dependency')}", "Priority: optional"]
    if r["depends"]: ctl.append("Depends: " + ", ".join(f"{d} (= {OSVER})" for d in r["depends"]))
    if r["provides"]: ctl.append("Provides: " + ", ".join(r["provides"]))
    if c.get("conflicts"): ctl.append("Conflicts: " + ", ".join(c["conflicts"].split()))
    ctl.append(f"NZ-Title: {c.get('title', deb)}")
    ctl.append(f"NZ-Contents: {contents}")
    ctl.append(f"Description: {desc}")
    control = "\n".join(ctl) + "\n"
    def add_ctl(t):
        b = control.encode(); ti = tarfile.TarInfo("./control"); ti.size = len(b); ti.mode = 0o644
        ti.mtime = int(time.time()); t.addfile(reset(ti), io.BytesIO(b))
    blob = b"!<arch>\n" + ar_member("debian-binary", b"2.0\n") + ar_member("control.tar.xz", tar_xz(add_ctl)) \
           + ar_member("data.tar.xz", tar_xz(add_data))
    fn = f"{deb}_{OSVER}_arm64.deb"
    repo = c.get("repo", "deps")
    if repo not in ("deps", "apps"): die(f"[{deb}] repo must be deps or apps")
    os.makedirs(os.path.join(OUT, repo), exist_ok=True)
    open(os.path.join(OUT, repo, fn), "wb").write(blob)
    index[repo].append(control + f"Filename: {fn}\nSize: {len(blob)}\nSHA256: {hashlib.sha256(blob).hexdigest()}\n")
    print(f"wrote {fn} ({len(blob)/1e6:.1f} MB)")
for repo in ("deps", "apps"):
    os.makedirs(os.path.join(OUT, repo), exist_ok=True)
    open(os.path.join(OUT, repo, "Packages"), "w").write("\n".join(index[repo]))
open(os.path.join(OUT, "base-files.txt"), "w").write("\n".join(sorted(base_files)) + "\n")
open(os.path.join(OUT, "packaged-files.txt"), "w").write("\n".join(sorted(f for fl in deb_files.values() for f in fl)) + "\n")
