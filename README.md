# NimbleZero-dependencies: package files

This branch holds the installable packages that the NimbleZero Store downloads: one
directory per package set, each with a `Packages` index and `.deb` files. The Store of a
system reads the set named in its `/etc/nz-release`.

| Directory | For |
|---|---|
| `0.2.0~dev1/` | first development image (ffmpeg 6.1) |
| `0.2.0~dev2/` | development images 2-4: ffmpeg 7.1 with the library names of Debian 13 |
| `0.2.0~dev3/` | development images 5-9: as dev2, PipeWire settings for the one system volume |
| `0.2/` | development image 10 and later: every package has its own version; adds CJK and fallback fonts, pygame, Python cryptography, libfmt 10. Since 2026-11-23 (image 11): Python 3.13, ALSA plugins, mpg123, libopenmpt, small libraries, Python modules for hardware and network, pip. Since 2026-11-27: libgme and libsidplayfp (chip music). Since 2026-11-28 (image 22): rebuilt with gcc 15; Bluetooth (BlueZ, D-Bus), camera (libcamera 0.8, rpicam-apps, picamera2, OpenCV), mpv, GStreamer, software radio, network tools, Wireshark, GPIO, Python D-Bus/GObject and more; their sources are the release `sources-0.2` |

How a set was built, licences and source code: `<set>/source-info/`.

Unofficial software for the M5Stack Cardputer Zero; not an M5Stack product. No warranty.
