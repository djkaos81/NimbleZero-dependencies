################################################################################
#
# python-pidng
#
################################################################################

PYTHON_PIDNG_VERSION = 4.0.9
PYTHON_PIDNG_SOURCE = pidng-4.0.9.tar.gz
PYTHON_PIDNG_SITE = https://files.pythonhosted.org/packages/c0/65/2670c465c8a63a23eb3a5e5547262e247e1aa2d3889a0a6781da9109d5f7
PYTHON_PIDNG_SETUP_TYPE = setuptools
PYTHON_PIDNG_LICENSE = MIT
PYTHON_PIDNG_LICENSE_FILES = LICENSE
PYTHON_PIDNG_DEPENDENCIES = python-numpy

$(eval $(python-package))
