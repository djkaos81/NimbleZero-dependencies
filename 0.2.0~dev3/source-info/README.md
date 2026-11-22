# Package set 0.2.0~dev3: how it was built

Development packages for the next NimbleZero version. They belong to one build of the
system and are only meant for the image built with them.

- Built with Buildroot 2026.02.3 plus the changes in `buildroot-patches/`, from the
  NimbleZero source tree, configuration `nz_full_defconfig` (full configuration as used:
  `buildroot.config`), with the option changes in `external.mk`.
- One build is cut into a base image and these packages by `make-packages.py` according
  to `groups.conf`; `provided.map` gives the Debian package names a library stands for.
- Every package and its licence: `licence-manifest.csv`; all licence texts:
  `licences.tar.gz`.
- Source code: unless listed here, the package versions are those of NimbleZero v0.1.0,
  whose complete source archive is attached to the v0.1.0 release
  (https://github.com/djkaos81/NimbleZero/releases/tag/v0.1.0). New or changed, with their
  sources (and the patches applied) in `sources-added/`: ffmpeg 7.1.5 (was 6.1.5),
  libidn2 2.3.8, Lua 5.4.8, PipeWire 1.2.8, WirePlumber 0.5.10.
- NimbleZero's own files in these packages (start script and settings for PipeWire,
  Snake) are GPL-2.0; their source is the files themselves, or `sdk/examples/snake.c` in
  the NimbleZero repository.

Against set 0.2.0~dev2 only NimbleZero's own files changed (PipeWire settings: full
volume at start, volume applied by PipeWire itself); all third-party sources are the same.
