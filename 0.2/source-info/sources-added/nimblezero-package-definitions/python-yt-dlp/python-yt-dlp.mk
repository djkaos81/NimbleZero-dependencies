################################################################################
#
# python-yt-dlp
#
################################################################################

PYTHON_YT_DLP_VERSION = 2026.11.23
PYTHON_YT_DLP_SOURCE = yt_dlp-2026.11.23.tar.gz
PYTHON_YT_DLP_SITE = https://files.pythonhosted.org/packages/c4/5a/1b6b13c8bf553841e7deaf204105dc63d4765aca9143def73a130da228c1
PYTHON_YT_DLP_SETUP_TYPE = hatch
PYTHON_YT_DLP_LICENSE = Unlicense
PYTHON_YT_DLP_LICENSE_FILES = LICENSE

$(eval $(python-package))
