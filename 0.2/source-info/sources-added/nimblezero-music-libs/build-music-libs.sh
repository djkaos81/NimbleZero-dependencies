#!/bin/sh
# Package set 0.2: libgme and libsidplayfp, built outside the set's Buildroot build
# (2026-11-27, for the Media Player's chip music) with the compiler of the NimbleZero SDK.
#
#   SDK=/path/to/nimblezero-sdk  sh build-music-libs.sh   -> pkgout/*.deb and Packages stanzas
#
# Sources: ../game-music-emu-0.6.5/ (git archive of tag 0.6.5 of
# https://github.com/libgme/game-music-emu) and ../libsidplayfp-2.16.1/ (release archive of
# https://github.com/libsidplayfp/libsidplayfp).  No patches.
# Versions: the newest releases with the library names of Debian 13 (libgme0,
# libsidplayfp6); Debian 13 itself has 0.6.3 and 2.12.0, with open security issues.
set -e
SDK=${SDK:?set SDK to the NimbleZero SDK}; H=$(cd "$(dirname "$0")" && pwd); W=$PWD/music-build
PY=$(command -v python3)                     # the build machine's, before the SDK's tools come first
PATH=$SDK/bin:$PATH
mkdir -p "$W" && cd "$W"
tar xzf "$H/../game-music-emu-0.6.5/game-music-emu-0.6.5.tar.gz"
tar xzf "$H/../libsidplayfp-2.16.1/libsidplayfp-2.16.1.tar.gz"

# libgme: CMake; YM2612 by the Nuked OPN2 emulator (LGPL-2.1+), zlib for .vgz
mkdir -p b-gme && (cd b-gme && cmake ../game-music-emu-0.6.5 -DCMAKE_TOOLCHAIN_FILE=$SDK/share/buildroot/toolchainfile.cmake \
	-DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_SHARED_LIBS=ON -DGME_BUILD_EXAMPLES=OFF -DGME_BUILD_TESTING=OFF \
	&& make -j"$(nproc)" && make install DESTDIR="$W/stage-gme")

# libsidplayfp: autotools; no libgcrypt (song length file: its own MD5), no exSID / HardSID
mkdir -p b-sid && (cd b-sid && ../libsidplayfp-2.16.1/configure --host=aarch64-linux --prefix=/usr --disable-static \
	--without-gcrypt --without-exsid --disable-hardsid CFLAGS=-O2 CXXFLAGS=-O2 && make -j"$(nproc)" && make install DESTDIR="$W/stage-sid")

for f in stage-gme/usr/lib/libgme.so.0.6.5 stage-sid/usr/lib/libsidplayfp.so.6.7.45; do
	aarch64-linux-strip --remove-section=.comment --remove-section=.note --strip-unneeded "$f"
done
"$PY" "$H/nz-pack.py" --name nz-lib-libgme --version 0.2.1 --title libgme \
	--description "Video game music library (libgme): NES, SNES, Genesis/VGM, Game Boy, PC Engine, MSX, ZX Spectrum, Atari" \
	--contents "game-music-emu 0.6.5" --provides "libgme0 (= 0.6.5)" --root stage-gme --out pkgout \
	usr/lib/libgme.so.0.6.5 usr/lib/libgme.so.0 usr/lib/libgme.so
"$PY" "$H/nz-pack.py" --name nz-lib-libsidplayfp --version 0.2.1 --title libsidplayfp \
	--description "Commodore 64 SID music library (libsidplayfp)" \
	--contents "libsidplayfp 2.16.1" --provides "libsidplayfp6 (= 2.16.1)" --root stage-sid --out pkgout \
	usr/lib/libsidplayfp.so.6.7.45 usr/lib/libsidplayfp.so.6 usr/lib/libsidplayfp.so
