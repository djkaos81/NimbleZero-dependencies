################################################################################
# nz-fonts-droid-fallback - Droid Sans Fallback (source: Debian's fonts-android tarball)
################################################################################
NZ_FONTS_DROID_FALLBACK_VERSION = 8.1.0r7
NZ_FONTS_DROID_FALLBACK_SITE = https://deb.debian.org/debian/pool/main/f/fonts-android
NZ_FONTS_DROID_FALLBACK_SOURCE = fonts-android_$(NZ_FONTS_DROID_FALLBACK_VERSION).orig.tar.gz
NZ_FONTS_DROID_FALLBACK_STRIP_COMPONENTS = 0
NZ_FONTS_DROID_FALLBACK_LICENSE = Apache-2.0
NZ_FONTS_DROID_FALLBACK_LICENSE_FILES = NOTICE

define NZ_FONTS_DROID_FALLBACK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/DroidSansFallbackFull.ttf $(TARGET_DIR)/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf
	$(INSTALL) -D -m 0644 $(@D)/DroidSansFallback.ttf $(TARGET_DIR)/usr/share/fonts-droid-fallback/truetype/DroidSansFallback.ttf
endef

$(eval $(generic-package))
