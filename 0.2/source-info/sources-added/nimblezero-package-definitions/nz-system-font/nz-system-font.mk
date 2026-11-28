################################################################################
#
# nz-system-font - /usr/share/nz/fonts/nz-8.nzf, read by nzui.h
#
# Fusion Pixel 8px (monospaced, BDF) is downloaded; NimbleZero Sans 8 and the key
# symbols are in src/.  scripts/make-nz-font.py puts them into one file.
#
################################################################################

NZ_SYSTEM_FONT_VERSION = 2026.07.20
NZ_SYSTEM_FONT_SITE = https://github.com/TakWolf/fusion-pixel-font/releases/download/$(NZ_SYSTEM_FONT_VERSION)
NZ_SYSTEM_FONT_SOURCE = fusion-pixel-font-8px-monospaced-bdf-v$(NZ_SYSTEM_FONT_VERSION).zip
NZ_SYSTEM_FONT_LICENSE = OFL-1.1 (NimbleZero Sans 8, Fusion Pixel and the fonts it is made from), GPL-2.0 or OFL-1.1 (key symbols)
NZ_SYSTEM_FONT_LICENSE_FILES = OFL.txt LICENSES/boutique-bitmap-7x7/OFL.txt LICENSES/galmuri/LICENSE.txt \
	LICENSES/misaki/misaki.txt LICENSES/miseki-bitmap/LICENSE.txt OFL-nimblezero-sans.txt
NZ_SYSTEM_FONT_DEPENDENCIES = host-python3
NZ_SYSTEM_FONT_SRC = $(BR2_EXTERNAL_NZ_PATH)/package/nz-system-font/src
NZ_SYSTEM_FONT_FUSION = $(@D)/fusion-pixel-8px-monospaced

define NZ_SYSTEM_FONT_EXTRACT_CMDS
	$(HOST_DIR)/bin/python3 -I -m zipfile -e $(NZ_SYSTEM_FONT_DL_DIR)/$(NZ_SYSTEM_FONT_SOURCE) $(@D)
	cp $(NZ_SYSTEM_FONT_SRC)/OFL-nimblezero-sans.txt $(@D)/
endef

define NZ_SYSTEM_FONT_BUILD_CMDS
	$(HOST_DIR)/bin/python3 -I $(BR2_EXTERNAL_NZ_PATH)/../scripts/make-nz-font.py $(@D)/nz-8.nzf \
		--base $(NZ_SYSTEM_FONT_SRC)/nimblezero-sans-8.bdf --keys $(NZ_SYSTEM_FONT_SRC)/nimblezero-keys-8.txt \
		--cjk ja=$(NZ_SYSTEM_FONT_FUSION)-ja.bdf --cjk zh-hans=$(NZ_SYSTEM_FONT_FUSION)-zh_hans.bdf \
		--cjk zh-hant=$(NZ_SYSTEM_FONT_FUSION)-zh_hant.bdf --cjk ko=$(NZ_SYSTEM_FONT_FUSION)-ko.bdf
endef

define NZ_SYSTEM_FONT_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/nz-8.nzf $(TARGET_DIR)/usr/share/nz/fonts/nz-8.nzf
	$(INSTALL) -D -m 0644 $(NZ_SYSTEM_FONT_SRC)/README $(TARGET_DIR)/usr/share/nz/fonts/README
	$(INSTALL) -D -m 0644 $(@D)/OFL-nimblezero-sans.txt $(TARGET_DIR)/usr/share/nz/fonts/OFL-nimblezero-sans.txt
	$(INSTALL) -D -m 0644 $(@D)/OFL.txt $(TARGET_DIR)/usr/share/nz/fonts/OFL-fusion-pixel.txt
	for f in boutique-bitmap-7x7/OFL.txt galmuri/LICENSE.txt misaki/misaki.txt miseki-bitmap/LICENSE.txt; do \
		$(INSTALL) -D -m 0644 $(@D)/LICENSES/$$f $(TARGET_DIR)/usr/share/nz/fonts/fusion-pixel-sources/$$f || exit 1; \
	done
endef

$(eval $(generic-package))
