################################################################################
#
# python-prctl
#
################################################################################

PYTHON_PRCTL_VERSION = 1.8.1
PYTHON_PRCTL_SOURCE = python-prctl-1.8.1.tar.gz
PYTHON_PRCTL_SITE = https://files.pythonhosted.org/packages/c0/99/be5393cfe9c16376b4f515d90a68b11f1840143ac1890e9008bc176cf6a6
PYTHON_PRCTL_SETUP_TYPE = setuptools
PYTHON_PRCTL_LICENSE = GPL (PyPI classifier; upstream: GPL-3.0+; no licence file in the archive)
PYTHON_PRCTL_LICENSE_FILES =
PYTHON_PRCTL_DEPENDENCIES = libcap

$(eval $(python-package))
