################################################################################
#
# libsidplayfp
#
################################################################################

LIBSIDPLAYFP_VERSION = 2.16.1
LIBSIDPLAYFP_SITE = https://github.com/libsidplayfp/libsidplayfp/releases/download/v$(LIBSIDPLAYFP_VERSION)
LIBSIDPLAYFP_LICENSE = GPL-2.0+
LIBSIDPLAYFP_LICENSE_FILES = COPYING
LIBSIDPLAYFP_INSTALL_STAGING = YES
# no libgcrypt (song-length file: its own MD5), no exSID / HardSID / USBSID hardware
LIBSIDPLAYFP_CONF_OPTS = --disable-static --without-gcrypt --without-exsid --without-usbsid --disable-hardsid

$(eval $(autotools-package))
