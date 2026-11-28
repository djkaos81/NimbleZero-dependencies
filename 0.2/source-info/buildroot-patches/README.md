# Changes to the pinned Buildroot tree

Applied to Buildroot (versions.env) before building: `git apply` in the Buildroot
directory, in order. `build.sh` does it when a patch is not applied yet.

| Patch | Why |
|---|---|
| 0001-ffmpeg-7.1.5 | ffmpeg 6.1.5 -> 7.1.5. Debian 13, which M5Stack's apps are built for, has ffmpeg 7.1; its libraries have other names (libavcodec.so.61 ...) than those of 6.1, and apps linked against them could not load. Six Buildroot patches that only concern x86, MIPS, VAAPI, MMAL or Blu-ray PCM code and no longer apply or matter here are dropped. |
| 0002-fmt-10.1.1 | fmt -> 10.1.1, the version Debian 13 ships (libfmt.so.10), for M5Stack apps linked against it (dev10). |
| 0003-python-3.13.16 | Python -> 3.13.16, Debian 13's minor version, so M5Stack's Python apps and modules match (dev11). |
| 0004-camera-rpi-fork-sdl2-mixer | Phase 4. libcamera v0.7.0 (linuxtv) -> Raspberry Pi's fork v0.8.0+rpt20261104 (the library M5Stack's camera apps link against, libcamera.so.0.8, with the Raspberry Pi controls); libcamera-apps -> rpicam-apps v1.15.0 with the Raspberry Pi features on (Wayland and Hailo off; the EGL preview only with libepoxy, which this build does not have); its two Buildroot patches are upstream or only matter with those features off, so they are dropped. sdl2_mixer 2.6.3 -> 2.8.1 (frotz-zero needs 2.8.1). PipeWire is built without its libcamera plugin, which does not build against libcamera 0.8. Both git sources are pinned by tag; the tarball hashes were computed locally. |
