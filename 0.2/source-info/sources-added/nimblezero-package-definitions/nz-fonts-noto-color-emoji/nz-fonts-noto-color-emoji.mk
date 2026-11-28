################################################################################
#
# nz-fonts-noto-color-emoji
#
################################################################################

# Upstream builds the colour font with tools outside Buildroot's reach; Debian 13's
# binary package carries the built file, so that package is the source here.
NZ_FONTS_NOTO_COLOR_EMOJI_VERSION = 2.051-0+deb13u1
NZ_FONTS_NOTO_COLOR_EMOJI_SOURCE = fonts-noto-color-emoji_$(NZ_FONTS_NOTO_COLOR_EMOJI_VERSION)_all.deb
NZ_FONTS_NOTO_COLOR_EMOJI_SITE = https://deb.debian.org/debian/pool/main/f/fonts-noto-color-emoji
NZ_FONTS_NOTO_COLOR_EMOJI_LICENSE = OFL-1.1 (font), Apache-2.0 (build tools, not included)
NZ_FONTS_NOTO_COLOR_EMOJI_LICENSE_FILES = usr/share/doc/fonts-noto-color-emoji/copyright
NZ_FONTS_NOTO_COLOR_EMOJI_EXTRACT_DEPENDENCIES = host-python3

define NZ_FONTS_NOTO_COLOR_EMOJI_EXTRACT_CMDS
	cd $(@D) && $(HOST_DIR)/bin/python3 -I -c 'import sys; d=open(sys.argv[1],"rb").read(); \
		i=d.index(b"data.tar."); n=d[i:i+16].split(b"/")[0].split(b" ")[0].decode(); \
		sz=int(d[i+48:i+58]); open(n,"wb").write(d[i+60:i+60+sz])' \
		$(NZ_FONTS_NOTO_COLOR_EMOJI_DL_DIR)/$(NZ_FONTS_NOTO_COLOR_EMOJI_SOURCE)
	tar -C $(@D) -xf $(@D)/data.tar.*
endef

define NZ_FONTS_NOTO_COLOR_EMOJI_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf \
		$(TARGET_DIR)/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf
endef

$(eval $(generic-package))
