################################################################################
#
# python-picamera2
#
################################################################################

PYTHON_PICAMERA2_VERSION = 0.3.39
PYTHON_PICAMERA2_SOURCE = picamera2-0.3.39.tar.gz
PYTHON_PICAMERA2_SITE = https://files.pythonhosted.org/packages/ac/cb/30e77272e014ee505d2c31f5ef1c6054582b0c94b4ad9f87330d723f0b65
PYTHON_PICAMERA2_SETUP_TYPE = setuptools
PYTHON_PICAMERA2_LICENSE = BSD-2-Clause
PYTHON_PICAMERA2_LICENSE_FILES = LICENSE

$(eval $(python-package))
