################################################################################
#
# python-libarchive-c
#
################################################################################

PYTHON_LIBARCHIVE_C_VERSION = 5.3
PYTHON_LIBARCHIVE_C_SOURCE = libarchive_c-5.3.tar.gz
PYTHON_LIBARCHIVE_C_SITE = https://files.pythonhosted.org/packages/26/23/e72434d5457c24113e0c22605cbf7dd806a2561294a335047f5aa8ddc1ca
PYTHON_LIBARCHIVE_C_SETUP_TYPE = setuptools
PYTHON_LIBARCHIVE_C_LICENSE = CC0-1.0
PYTHON_LIBARCHIVE_C_LICENSE_FILES = LICENSE.md

$(eval $(python-package))
