# NimbleZero-dependencies: package files

This branch holds the installable packages that the NimbleZero Store downloads: one
directory per package set, each with a `Packages` index and `.deb` files. A package set
belongs to one version of the system; the Store reads the set its image was built with.

| Directory | For |
|---|---|
| `0.2.0~dev1/` | first development image (ffmpeg 6.1) |
| `0.2.0~dev2/` | development image 2: ffmpeg 7.1 with the library names of Debian 13 |

How a set was built, licences and source code: `<set>/source-info/`.

Unofficial software for the M5Stack Cardputer Zero; not an M5Stack product. No warranty.
