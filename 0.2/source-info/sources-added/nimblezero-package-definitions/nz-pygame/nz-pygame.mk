################################################################################
# nz-pygame - pygame (Buildroot keeps the name python-pygame as a removed, "legacy" option)
################################################################################
NZ_PYGAME_VERSION = 2.6.1
NZ_PYGAME_SOURCE = pygame-$(NZ_PYGAME_VERSION).tar.gz
NZ_PYGAME_SITE = https://files.pythonhosted.org/packages/source/p/pygame
NZ_PYGAME_SETUP_TYPE = setuptools
NZ_PYGAME_LICENSE = LGPL-2.1+
NZ_PYGAME_LICENSE_FILES = docs/LGPL.txt
NZ_PYGAME_DEPENDENCIES = sdl2 sdl2_image sdl2_mixer sdl2_ttf freetype libpng jpeg host-pkgconf
# pygame's own configuration step looks for the libraries itself: point it at the
# staging directory instead of the build machine's /usr.
NZ_PYGAME_ENV = \
	SDL_CONFIG=$(STAGING_DIR)/usr/bin/sdl2-config \
	LOCALBASE=$(STAGING_DIR)/usr \
	PYGAME_EXTRA_BASE=$(STAGING_DIR)/usr \
	PORTMIDI_INC_PORTTIME=1

# ... and stop it from adding the build machine's own directories
define NZ_PYGAME_NO_HOST_DIRS
	$(SED) '/^extrabases.extend(("\/usr", "\/usr\/local"))/d' \
		-e "s|inc = '-I' + '/usr/X11R6/include'|inc = ''|" $(@D)/buildconfig/config_unix.py
endef
NZ_PYGAME_POST_PATCH_HOOKS += NZ_PYGAME_NO_HOST_DIRS

# Not for a device: the documentation, the test suite, the examples, and the clipboard
# module (it is the only part that needs X11).
define NZ_PYGAME_TRIM
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/pygame/docs \
		$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/pygame/tests \
		$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/pygame/examples \
		$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/pygame/scrap.*.so
endef
NZ_PYGAME_POST_INSTALL_TARGET_HOOKS += NZ_PYGAME_TRIM

$(eval $(python-package))
