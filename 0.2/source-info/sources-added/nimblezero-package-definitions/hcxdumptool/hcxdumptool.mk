################################################################################
#
# hcxdumptool
#
################################################################################

HCXDUMPTOOL_VERSION = 8.0.0
HCXDUMPTOOL_SITE = https://github.com/ZerBea/hcxdumptool/releases/download/$(HCXDUMPTOOL_VERSION)
HCXDUMPTOOL_LICENSE = MIT
HCXDUMPTOOL_LICENSE_FILES = license.txt
HCXDUMPTOOL_DEPENDENCIES = libpcap

define HCXDUMPTOOL_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) CC="$(TARGET_CC)" CFLAGS="$(TARGET_CFLAGS)" LDFLAGS="$(TARGET_LDFLAGS) -lpcap"
endef

define HCXDUMPTOOL_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) DESTDIR=$(TARGET_DIR) PREFIX=/usr install
endef

$(eval $(generic-package))
