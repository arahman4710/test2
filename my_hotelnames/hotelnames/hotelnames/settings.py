# Scrapy settings for hotelnames project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hotelnames'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['hotelnames.spiders']
NEWSPIDER_MODULE = 'hotelnames.spiders'
DEFAULT_ITEM_CLASS = 'hotelnames.items.HotelnameItem'
# USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
USER_AGENT = "Mozilla/4.0 (compatible;MSIE 7.0;Windows NT 6.0)"
SCHEDULER_ORDER='BFO'
LOG_ENABLED=True
LOG_FILE="scrapy-hotelnames.log"
LOG_LEVEL='INFO'


