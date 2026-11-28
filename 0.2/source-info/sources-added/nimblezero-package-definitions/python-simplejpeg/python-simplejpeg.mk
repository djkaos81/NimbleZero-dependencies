################################################################################
#
# python-simplejpeg
#
################################################################################

PYTHON_SIMPLEJPEG_VERSION = 1.10.1
PYTHON_SIMPLEJPEG_SOURCE = simplejpeg-1.10.1.tar.gz
PYTHON_SIMPLEJPEG_SITE = https://files.pythonhosted.org/packages/e2/a8/0eb3b52f208f3ba8274d53bf90c655125d0c863551834144c95ecc8f6a32
PYTHON_SIMPLEJPEG_SETUP_TYPE = setuptools
PYTHON_SIMPLEJPEG_LICENSE = MIT
PYTHON_SIMPLEJPEG_LICENSE_FILES = LICENSE
PYTHON_SIMPLEJPEG_DEPENDENCIES = host-python-numpy host-python-cython python-numpy jpeg
PYTHON_SIMPLEJPEG_ENV = SIMPLEJPEG_DYNAMIC_LINKING=1

$(eval $(python-package))
