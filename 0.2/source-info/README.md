# Package set 0.2: how it was built

Development packages for the next NimbleZero version (the 0.2 line). From this set on,
every package has its own version (`0.2.N`): a package is published again only when its
contents changed, and devices download only what changed.

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
  sources (and the patches applied) in `sources-added/`:
  - as in set 0.2.0~dev3: ffmpeg 7.1.5, libidn2 2.3.8, Lua 5.4.8, PipeWire 1.2.8,
    WirePlumber 0.5.10;
  - new in 0.2: fmt 10.1.1, pygame 2.6.1, Python cryptography 46.0.3 and bcrypt 5.0.0
    (each archive includes the Rust crates it was built with), cffi 2.0.0,
    pycparser 2.23, Droid Sans Fallback (Debian's fonts-android 8.1.0r7 archive),
    Noto Sans CJK 2.004 (unmodified upstream font files; see the README there).
  - added 2026-11-23 (compatibility phase 3): Python 3.13.16 (Debian 13 has Python 3.13;
    `buildroot-patches/0003` replaces Buildroot's 3.14), alsa-plugins, libusb, libuv,
    yaml-cpp, mpg123, libopenmpt, cJSON, c-ares, and the Python modules serial, spidev,
    smbus2, pyudev, netifaces, aiohttp with what it needs, websockets, websocket-client,
    zeroconf, mutagen, pip, setuptools. iproute2 is listed because it is in the base
    system from this build on.
  - added 2026-11-27 (Media Player 0.5: chip music), **built outside the Buildroot build**:
    game-music-emu (libgme) 0.6.5 and libsidplayfp 2.16.1, packages `nz-lib-libgme` and
    `nz-lib-libsidplayfp`. They were compiled with the NimbleZero SDK's compiler by
    `sources-added/nimblezero-music-libs/build-music-libs.sh`, which also writes the
    packages (`nz-pack.py`: the control fields and NZ-Digest of `make-packages.py`); the
    build is reproducible (same digests). `make-packages.py` does not know these two:
    when it writes this set again, their entries in `Packages` and their `.deb` files
    must be carried over (or the libraries added to the Buildroot build).
- How NimbleZero builds the packages that are not in Buildroot (fonts, pygame, PipeWire
  start-up): `sources-added/nimblezero-package-definitions/`.
- NimbleZero's own files in these packages (start script and settings for PipeWire,
  Snake) are GPL-2.0; their source is the files themselves, or `sdk/examples/snake.c` in
  the NimbleZero repository.
- The Rust compiler used on the build machine (Rust 1.88.0, pre-built) is not part of any
  package.
