################################################################################
#
# hcxtools
#
################################################################################

HCXTOOLS_VERSION = 8.0.0
HCXTOOLS_SITE = https://github.com/ZerBea/hcxtools/releases/download/$(HCXTOOLS_VERSION)
HCXTOOLS_LICENSE = MIT
HCXTOOLS_LICENSE_FILES = license.txt
HCXTOOLS_DEPENDENCIES = host-pkgconf openssl zlib libcurl

$(eval $(meson-package))
