################################################################################
#
# libgme (game-music-emu)
#
################################################################################

LIBGME_VERSION = 0.6.5
LIBGME_SITE = https://github.com/libgme/game-music-emu.git
LIBGME_SITE_METHOD = git
LIBGME_LICENSE = LGPL-2.1+
LIBGME_LICENSE_FILES = license.txt
LIBGME_INSTALL_STAGING = YES
LIBGME_DEPENDENCIES = zlib
# YM2612 by the Nuked OPN2 emulator (LGPL-2.1+); not MAME's, which would make the library GPL
LIBGME_CONF_OPTS = -DGME_BUILD_SHARED=ON -DGME_BUILD_STATIC=OFF -DGME_BUILD_EXAMPLES=OFF \
	-DGME_BUILD_TESTING=OFF -DGME_ENABLE_UBSAN=OFF -DGME_YM2612_EMU=Nuked

# 0001-*.patch: YM2413 by emu2413 (MIT, gme/ext/), instead of the release's stub

$(eval $(cmake-package))
