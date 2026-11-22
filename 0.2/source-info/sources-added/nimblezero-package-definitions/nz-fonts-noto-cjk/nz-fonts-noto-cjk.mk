################################################################################
# nz-fonts-noto-cjk - Noto Sans CJK collection files (regular, medium, bold)
################################################################################
NZ_FONTS_NOTO_CJK_VERSION = 2.004
NZ_FONTS_NOTO_CJK_SITE = https://raw.githubusercontent.com/notofonts/noto-cjk/Sans$(NZ_FONTS_NOTO_CJK_VERSION)/Sans/OTC
NZ_FONTS_NOTO_CJK_SOURCE = NotoSansCJK-Regular.ttc
NZ_FONTS_NOTO_CJK_EXTRA_DOWNLOADS = NotoSansCJK-Medium.ttc NotoSansCJK-Bold.ttc \
	https://raw.githubusercontent.com/notofonts/noto-cjk/Sans$(NZ_FONTS_NOTO_CJK_VERSION)/LICENSE
NZ_FONTS_NOTO_CJK_LICENSE = OFL-1.1
NZ_FONTS_NOTO_CJK_LICENSE_FILES = LICENSE

define NZ_FONTS_NOTO_CJK_EXTRACT_CMDS
	cp $(NZ_FONTS_NOTO_CJK_DL_DIR)/NotoSansCJK-Regular.ttc $(NZ_FONTS_NOTO_CJK_DL_DIR)/NotoSansCJK-Medium.ttc \
		$(NZ_FONTS_NOTO_CJK_DL_DIR)/NotoSansCJK-Bold.ttc $(NZ_FONTS_NOTO_CJK_DL_DIR)/LICENSE $(@D)/
endef

define NZ_FONTS_NOTO_CJK_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 -t $(TARGET_DIR)/usr/share/fonts/opentype/noto $(@D)/NotoSansCJK-Regular.ttc \
		$(@D)/NotoSansCJK-Medium.ttc $(@D)/NotoSansCJK-Bold.ttc
endef

$(eval $(generic-package))
