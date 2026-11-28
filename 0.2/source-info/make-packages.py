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

Versions: every package has its own.  SERIES is the package set's name (the directory
devices read, e.g. 0.2); a package's version is SERIES.N.  With --previous DIR (the set
as published: DIR/deps and DIR/apps with their Packages files and .deb files) a package
whose files and control data are unchanged keeps its version and its published file;
a package of the previous set that this build does not make at all (an app from
NimbleZero-apps, nz-store, a library built elsewhere) is carried over as it is
(carried.txt lists them);
a changed or new one gets the next N.  Devices then download only what changed.

Moved files: a file that an earlier published package had and that is now in another
package can only be installed over it if the new package says so (Replaces); dpkg
refuses otherwise ("trying to overwrite ..., which is also in package ...").  With
--history DIR (repeatable; a directory with .deb files of an earlier set) and the
--previous set, every such move is found and declared.

usage: make-packages.py O SHOW_INFO.json GROUPS.conf PROVIDED.map SERIES OUTDIR [--previous DIR] [--history DIR]... [--check-only]
"""
import sys, os, json, re, io, tarfile, hashlib, lzma, stat, struct, time, collections, fnmatch

def die(m): sys.exit("make-packages: " + m)

if len(sys.argv) < 7: die(__doc__)
O, INFO, GROUPS, PROVIDED, OSVER, OUT = sys.argv[1:7]
CHECK_ONLY = "--check-only" in sys.argv
PREV = sys.argv[sys.argv.index("--previous") + 1] if "--previous" in sys.argv else None
HISTORY = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--history"]
T = os.path.join(O, "target")
info = json.load(open(INFO))
target_pkgs = {k for k, v in info.items() if v.get("type") == "target"}

# ---- groups.conf ---------------------------------------------------------------------
# [base]            roots = a b c
# [nz-name]         packages = a b     depends = nz-x     section = dependency|runtime
#                   wants = nz-a | nz-b     installed along by the Store (the first of
#                       them, unless one is there already) but not required by dpkg
#                       (field NZ-Wants): for two packages that need each other, where
#                       a Depends in both directions could not be installed one by one
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
        # Python modules are shipped compiled only: Buildroot compiles X.py to X.pyc and
        # deletes X.py when the target is finished, after the file lists were written.
        # The .pyc belongs to the package that installed the .py.  (Up to set 0.2.0~dev3
        # these files stayed in the base image: 31 MB, and the base then claimed to
        # provide every Python module of every package.)
        if p is None and rel.endswith(".pyc"): p = file_pkg.get(rel[:-1])
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
    names, proof, src, *claim = l.split("|")
    rel = proof.lstrip("/")
    for deb, fl in deb_files.items():
        if rel in fileset[deb] or "usr/" + rel in fileset[deb] or any(f.startswith(rel + "/") for f in fl):
            ver = info.get(src, {}).get("version", OSVER) if not src.startswith("@") else OSVER
            if claim and claim[0].strip(): ver = claim[0].strip().replace("@", ver)   # Debian's version, stated on purpose ("1:@": epoch + real version)
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

# A package can only bring files into the directories the package layer covers.
LAYER = ("usr/", "etc/", "opt/", "lib/", "bin/", "sbin/", "var/")   # var: writable on its own
for deb, fl in deb_files.items():
    bad = [f for f in fl if not f.startswith(LAYER)]
    if bad: die(f"{deb}: files outside the package layer's directories (e.g. /{bad[0]}); it could not be installed")

# ---- versions: what was published before -----------------------------------------------
prev = {}                                    # deb -> (version, digest, repo, filename, stanza)
if PREV:
    for repo in ("deps", "apps"):
        f = os.path.join(PREV, repo, "Packages")
        if not os.path.exists(f): continue
        for st in open(f).read().split("\n\n"):
            d = dict(l.split(": ", 1) for l in st.splitlines() if ": " in l and not l.startswith(" "))
            if "Package" in d: prev[d["Package"]] = (d.get("Version", ""), d.get("NZ-Digest", ""), repo, d.get("Filename", ""), st.strip("\n") + "\n")
# ---- files that moved from one package to another ---------------------------------------
def deb_contents(path):
    """(package name, set of files and links) of a .deb file; dpkg-deb reads every
    compression in use (ours are xz, the apps' are zstd)"""
    import subprocess
    try:
        name = subprocess.run(["dpkg-deb", "-f", path, "Package"], check=True, capture_output=True, text=True).stdout.strip()
        raw = subprocess.run(["dpkg-deb", "--fsys-tarfile", path], check=True, capture_output=True).stdout
    except (OSError, subprocess.CalledProcessError) as e: die(f"cannot read {path}: {e}")
    with tarfile.open(fileobj=io.BytesIO(raw)) as t:
        return name, {m.name.lstrip("./") for m in t.getmembers() if not m.isdir()}
old_owner = collections.defaultdict(set)     # file -> packages that had it in an earlier publication
olddirs = list(HISTORY) + ([os.path.join(PREV, r) for r in ("deps", "apps")] if PREV else [])
for d in olddirs:
    if not os.path.isdir(d): die(f"no such directory: {d}")
    for fn in sorted(os.listdir(d)):
        if fn.endswith(".deb"):
            n, fl = deb_contents(os.path.join(d, fn))
            for f in fl: old_owner[f].add(n)
replaces = collections.defaultdict(set)      # deb -> packages it takes files over from
moved = {}
for deb, fl in deb_files.items():
    for f in fl:
        for q in old_owner.get(f, ()):
            if q != deb: replaces[deb].add(q); moved.setdefault((deb, q), f)
for (deb, q), f in sorted(moved.items()): print(f"moved: {deb} takes over from {q} (e.g. /{f})")

def digest(deb, meta):
    """Identity of a package: its files (path, mode, contents) and its control data without versions."""
    h = hashlib.sha256(meta.encode())
    for rel in sorted(deb_files[deb]):
        fp = os.path.join(T, rel); st = os.lstat(fp)
        h.update(f"{rel}\0{stat.S_IMODE(st.st_mode):o}\0".encode())
        if stat.S_ISLNK(st.st_mode): h.update(b"L" + os.readlink(fp).encode())
        else: h.update(hashlib.sha256(open(fp, "rb").read()).digest())
    return h.hexdigest()
def next_version(deb):
    m = re.match(re.escape(OSVER) + r"\.(\d+)$", prev.get(deb, ("",))[0])
    return f"{OSVER}.{int(m.group(1)) + 1 if m else 1}"
plan = {}                                    # deb -> dict(version, digest, reuse, lines)
for deb, r in rep["packages"].items():
    c = groups.get(deb, {}); brp = r["buildroot_packages"]
    desc = c.get("description") or ("Library package built from " + ", ".join(brp))
    contents = ", ".join(f"{p} {info[p].get('version','')}".strip() for p in brp)
    meta = "\n".join([deb, "depends " + " ".join(r["depends"]), "provides " + " ".join(r["provides"]),
                      "conflicts " + c.get("conflicts", ""), *(["wants " + " ".join(c["wants"].split())] if c.get("wants") else []), *(["replaces " + " ".join(sorted(replaces[deb]))] if replaces[deb] else []), "section " + ("libs" if r["library"] else c.get("section", "dependency")),
                      "title " + c.get("title", deb), "contents " + contents, "description " + desc])
    dg = digest(deb, meta)
    reuse = deb in prev and prev[deb][1] == dg and os.path.exists(os.path.join(PREV, prev[deb][2], prev[deb][3]))
    plan[deb] = {"version": prev[deb][0] if reuse else next_version(deb), "digest": dg, "reuse": reuse, "desc": desc, "contents": contents}

# ---- write .deb files and the index --------------------------------------------------
index = collections.defaultdict(list)       # repository (deps | apps) -> index entries
changed = []
for deb, r in rep["packages"].items():
    c = groups.get(deb, {}); files = sorted(deb_files[deb]); pl = plan[deb]
    repo = c.get("repo", "deps")
    if repo not in ("deps", "apps"): die(f"[{deb}] repo must be deps or apps")
    os.makedirs(os.path.join(OUT, repo), exist_ok=True)
    if pl["reuse"]:
        v, _, prepo, pfn, stanza = prev[deb]
        blob = open(os.path.join(PREV, prepo, pfn), "rb").read()
        open(os.path.join(OUT, repo, pfn), "wb").write(blob)
        index[repo].append(stanza)
        print(f"kept  {pfn} (unchanged)")
        continue
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
    ver = pl["version"]
    ctl = [f"Package: {deb}", f"Version: {ver}", "Architecture: arm64",
           "Maintainer: NimbleZero <https://github.com/djkaos81/NimbleZero>",
           f"Installed-Size: {max(1, r['bytes'] // 1024)}",
           f"Section: {'libs' if r['library'] else c.get('section', 'dependency')}", "Priority: optional"]
    # "at least the version this was built with": a package and the libraries it was cut with
    if r["depends"]: ctl.append("Depends: " + ", ".join(f"{d} (>= {plan[d]['version']})" for d in r["depends"]))
    if r["provides"]: ctl.append("Provides: " + ", ".join(r["provides"]))
    if c.get("conflicts"): ctl.append("Conflicts: " + ", ".join(c["conflicts"].split()))
    if c.get("wants"): ctl.append("NZ-Wants: " + " ".join(c["wants"].split()))
    # the versions of the other package that had the files: all before its current one
    if replaces[deb]: ctl.append("Replaces: " + ", ".join(f"{q} (<< {plan[q]['version']})" if q in plan else q for q in sorted(replaces[deb])))
    ctl.append(f"NZ-Title: {c.get('title', deb)}")
    ctl.append(f"NZ-Contents: {pl['contents']}")
    ctl.append(f"NZ-Digest: {pl['digest']}")
    ctl.append(f"Description: {pl['desc']}")
    control = "\n".join(ctl) + "\n"
    def add_ctl(t):
        b = control.encode(); ti = tarfile.TarInfo("./control"); ti.size = len(b); ti.mode = 0o644
        ti.mtime = int(time.time()); t.addfile(reset(ti), io.BytesIO(b))
    blob = b"!<arch>\n" + ar_member("debian-binary", b"2.0\n") + ar_member("control.tar.xz", tar_xz(add_ctl)) \
           + ar_member("data.tar.xz", tar_xz(add_data))
    fn = f"{deb}_{ver}_arm64.deb"
    open(os.path.join(OUT, repo, fn), "wb").write(blob)
    index[repo].append(control + f"Filename: {fn}\nSize: {len(blob)}\nSHA256: {hashlib.sha256(blob).hexdigest()}\n")
    changed.append(f"{deb} {ver}")
    print(f"wrote {fn} ({len(blob)/1e6:.1f} MB)")
# Packages of the previous set that this build does not make (apps built in NimbleZero-apps,
# the Store's own package, libraries built outside Buildroot) are carried over unchanged:
# their index entry and their file.  Without this, a rebuild of the set would drop them.
carried = []
for deb, (v, _, prepo, pfn, stanza) in sorted(prev.items()):
    if deb in rep["packages"]: continue
    src = os.path.join(PREV, prepo, pfn)
    if not os.path.exists(src): die(f"previous set lists {pfn}, which is not in {os.path.join(PREV, prepo)}")
    os.makedirs(os.path.join(OUT, prepo), exist_ok=True)
    open(os.path.join(OUT, prepo, pfn), "wb").write(open(src, "rb").read())
    index[prepo].append(stanza); carried.append(f"{deb} {v} ({prepo})")
    print(f"carried {pfn} (not made by this build)")
open(os.path.join(OUT, "carried.txt"), "w").write("\n".join(carried) + ("\n" if carried else ""))
print(f"{len(changed)} package(s) new or changed, {len(plan) - len(changed)} kept, {len(carried)} carried over")
open(os.path.join(OUT, "changed.txt"), "w").write("\n".join(changed) + "\n")
for repo in ("deps", "apps"):
    os.makedirs(os.path.join(OUT, repo), exist_ok=True)
    open(os.path.join(OUT, repo, "Packages"), "w").write("\n".join(index[repo]))
open(os.path.join(OUT, "base-files.txt"), "w").write("\n".join(sorted(base_files)) + "\n")
open(os.path.join(OUT, "packaged-files.txt"), "w").write("\n".join(sorted(f for fl in deb_files.values() for f in fl)) + "\n")
