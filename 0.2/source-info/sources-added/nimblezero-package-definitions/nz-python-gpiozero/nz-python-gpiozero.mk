################################################################################
#
# nz-python-gpiozero
#
################################################################################

NZ_PYTHON_GPIOZERO_VERSION = 2.0.1.post3
NZ_PYTHON_GPIOZERO_SOURCE = gpiozero-2.0.1.post3.tar.gz
NZ_PYTHON_GPIOZERO_SITE = https://files.pythonhosted.org/packages/67/63/864a3c36842cf7b05808aadf906763a024a1b13f2a4c8144e3163de91255
NZ_PYTHON_GPIOZERO_SETUP_TYPE = setuptools
NZ_PYTHON_GPIOZERO_LICENSE = BSD-3-Clause
NZ_PYTHON_GPIOZERO_LICENSE_FILES = LICENSE.rst

$(eval $(python-package))
