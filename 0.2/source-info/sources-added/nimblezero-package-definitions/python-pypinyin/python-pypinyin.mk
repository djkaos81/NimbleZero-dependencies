################################################################################
#
# python-pypinyin
#
################################################################################

PYTHON_PYPINYIN_VERSION = 0.55.0
PYTHON_PYPINYIN_SOURCE = pypinyin-0.55.0.tar.gz
PYTHON_PYPINYIN_SITE = https://files.pythonhosted.org/packages/b4/a4/784cf98c09e0dc22776b0d7d8a4a5b761218bcae4608c2416ce1e167c8af
PYTHON_PYPINYIN_SETUP_TYPE = setuptools
PYTHON_PYPINYIN_LICENSE = MIT
PYTHON_PYPINYIN_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
