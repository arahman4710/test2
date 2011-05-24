# Scrapy settings for hotwire_api project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hotwire_api'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['hotwire_api.spiders']
NEWSPIDER_MODULE = 'hotwire_api.spiders'
DEFAULT_ITEM_CLASS = 'hotwire_api.items.HotwireApiItem'
USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.224 Safari/534.10"
SCHEDULER_ORDER='BFO'

LOG_LEVEL = 'INFO'

LOG_FILE = 'hotwire-scraping.log'
