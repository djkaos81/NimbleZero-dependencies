include $(sort $(wildcard $(BR2_EXTERNAL_NZ_PATH)/package/*/*.mk))

# Build the Raspberry Pi overlays from the very kernel tree we boot (instead of
# taking prebuilt ones from the firmware repository, which belong to another
# kernel build) and stage them for the boot partition.
define NZ_LINUX_BUILD_OVERLAYS
	$(LINUX_MAKE_ENV) $(BR2_MAKE) $(LINUX_MAKE_FLAGS) -C $(LINUX_DIR) dtbs
	mkdir -p $(BINARIES_DIR)/rpi-firmware/overlays
	cp $(LINUX_DIR)/arch/arm64/boot/dts/overlays/*.dtb* $(BINARIES_DIR)/rpi-firmware/overlays/
	cp $(LINUX_DIR)/arch/arm64/boot/dts/overlays/README $(BINARIES_DIR)/rpi-firmware/overlays/ 2>/dev/null || true
endef
LINUX_POST_INSTALL_IMAGES_HOOKS += NZ_LINUX_BUILD_OVERLAYS

# Debian programs link libjpeg.so.62 (libjpeg62-turbo).  Buildroot builds libjpeg-turbo with
# the "JPEG 8" interface (libjpeg.so.8); the later option wins, giving Debian's library name.
JPEG_TURBO_CONF_OPTS += -DWITH_JPEG8=OFF

# --- Installable packages (scripts/make-packages.py) ----------------------------------
# All packages are cut from one build, so a library that is merely present must not be
# picked up by programs of another package or of the base.  Buildroot enables such
# optional features automatically; these lines switch off the ones that would tie
# packages together for no good reason (later options win).
# base: util-linux without the lastlog database (SQLite) and the Python bindings
UTIL_LINUX_CONF_OPTS += --disable-liblastlog2 --without-python --disable-pylibmount
UTIL_LINUX_LIBS_CONF_OPTS += --disable-liblastlog2 --without-python
# M5Stack runtime: libinput without Lua plugins
LIBINPUT_CONF_OPTS += -Dlua-plugins=disabled
# D-Bus without X11 autolaunch
DBUS_CONF_OPTS += --without-x
# Pillow without screen grabbing through X11
PYTHON_PILLOW_BUILD_OPTS := $(filter-out -Cxcb=enable,$(PYTHON_PILLOW_BUILD_OPTS)) -Cxcb=disable
# ffmpeg without the SDL2 output device and the libv4l2 wrapper (its own V4L2 input stays)
FFMPEG_CONF_OPTS += --disable-sdl2 --disable-libv4l2
# PipeWire without the ffmpeg plugin
PIPEWIRE_CONF_OPTS += -Dffmpeg=disabled -Dpw-cat-ffmpeg=disabled
