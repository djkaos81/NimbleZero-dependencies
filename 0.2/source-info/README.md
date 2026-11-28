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
  - **rebuilt 2026-11-28 (phase 4), all packages from one clean build** with the
    Bootlin bleeding-edge toolchain 2025.08-1 (gcc 15.1, glibc 2.41). libgme and
    libsidplayfp are Buildroot packages from this date on (same versions; their
    definitions are in `sources-added/nimblezero-package-definitions/`).
    **The sources of the 124 packages that are new or changed on this date are not in
    this directory** (631 MB; one archive is over GitHub's file limit for repositories):
    they are the release asset `nimblezero-0.2-sources-2026-11-28.tar` (SHA-256
    `6d7ed289a5c8c68501c9c67a040e2549e17e06631d748bf6cc7355915a57aa62`) of the release
    `sources-0.2` of this repository:
    https://github.com/djkaos81/nimblezero-dependencies/releases/tag/sources-0.2
    New: BlueZ 5.79, D-Bus, dbus-python, PyGObject and gobject-introspection, bleak,
    libcamera (Raspberry Pi's fork 0.8.0+rpt20261104, `buildroot-patches/0004`),
    rpicam-apps 1.15.0, picamera2 0.3.39, OpenCV 4.13, Boost, mpv 0.40, GStreamer 1.24
    with base, good and libav plugins, SDL2_mixer 2.8.1, SoX, FluidSynth, PortAudio,
    librtlsdr, rtl_433, HackRF, FFTW, tcpdump, nmap, arp-scan, nftables, ebtables,
    bridge-utils, wireless_tools, lldpd, dnsmasq, Wireshark, scapy, aircrack-ng, reaver,
    hcxtools, hcxdumptool, libgpiod 2, gpiod, RPi.GPIO, gpiozero, OpenSSH (client),
    tmux, git, dosfstools, acl, libcap, fbset, dtc, usb_modeswitch, sshpass, kbd,
    Tesseract with English, ZBar, yt-dlp, PyMuPDF, Noto Color Emoji (Debian's
    fonts-noto-color-emoji 2.051 archive, unmodified font), Python modules (PyYAML,
    psutil, wcwidth, h2, h11, aiofiles, cachetools, jsonschema, markdown-it, pypinyin
    and what they need) and the libraries these need; the full list with versions is
    the archive's `sources/` directory, licences are in `licence-manifest.csv`.
    `licence-manifest.csv`, `licences.tar.gz`, `buildroot.config` and the other build
    files here describe the build of 2026-11-28.
- How NimbleZero builds the packages that are not in Buildroot (fonts, pygame, PipeWire
  start-up): `sources-added/nimblezero-package-definitions/`.
- NimbleZero's own files in these packages (start script and settings for PipeWire,
  Snake) are GPL-2.0; their source is the files themselves, or `sdk/examples/snake.c` in
  the NimbleZero repository.
- The Rust compiler used on the build machine (Rust 1.88.0, pre-built) is not part of any
  package.
