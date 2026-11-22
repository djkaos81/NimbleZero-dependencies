# Changes to the pinned Buildroot tree

Applied to Buildroot (versions.env) before building: `git apply` in the Buildroot
directory, in order. `build.sh` does it when a patch is not applied yet.

| Patch | Why |
|---|---|
| 0001-ffmpeg-7.1.5 | ffmpeg 6.1.5 -> 7.1.5. Debian 13, which M5Stack's apps are built for, has ffmpeg 7.1; its libraries have other names (libavcodec.so.61 ...) than those of 6.1, and apps linked against them could not load. Six Buildroot patches that only concern x86, MIPS, VAAPI, MMAL or Blu-ray PCM code and no longer apply or matter here are dropped. |
