################################################################################
# nz-pipewire-conf - PipeWire start-up for a device without a login session
################################################################################
NZ_PIPEWIRE_CONF_VERSION = 0.1
NZ_PIPEWIRE_CONF_SITE = $(BR2_EXTERNAL_NZ_PATH)/package/nz-pipewire-conf/files
NZ_PIPEWIRE_CONF_SITE_METHOD = local
NZ_PIPEWIRE_CONF_LICENSE = GPL-2.0
NZ_PIPEWIRE_CONF_DEPENDENCIES = pipewire wireplumber

define NZ_PIPEWIRE_CONF_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/S50pipewire $(TARGET_DIR)/etc/init.d/S50pipewire
	$(INSTALL) -D -m 0644 $(@D)/pulse-nz.conf $(TARGET_DIR)/usr/share/pipewire/pipewire-pulse.conf.d/10-nz.conf
	$(INSTALL) -D -m 0644 $(@D)/wireplumber-nz.conf $(TARGET_DIR)/usr/share/wireplumber/wireplumber.conf.d/10-nz.conf
endef

$(eval $(generic-package))
