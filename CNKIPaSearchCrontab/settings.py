# -*- coding: utf-8 -*-

# Scrapy settings for CNKIPaSearchCrontab project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
BOT_NAME = 'CNKIPaSearchCrontab'

SPIDER_MODULES = ['CNKIPaSearchCrontab.spiders']
NEWSPIDER_MODULE = 'CNKIPaSearchCrontab.spiders'



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'CNKIPaSearchCrontab (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# BASEDIR = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
BASEDIR = os.path.abspath(os.path.join(os.getcwd(), '..'))

# 最大重试次数
MAX_RETRY_TIMES = 30
# 每个页面的专利个数
PATENT_NUMBER_PER_PAGE = 20

DOWNLOADER_MIDDLEWARES = {
    'CNKIPaSearchCrontab.middlewares.GetFromLocalityMiddleware': 543,
    'CNKIPaSearchCrontab.middlewares.RetryOrErrorMiddleware': 550,
    'CNKIPaSearchCrontab.middlewares.ProxyMiddleware': 843,
    'CNKIPaSearchCrontab.middlewares.CookieMiddleware': 844,

}
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'CNKIPaSearchCrontab.pipelines.PageJsonPipeline': 300,
    'CNKIPaSearchCrontab.pipelines.FilterPipeline': 301,
    'CNKIPaSearchCrontab.pipelines.MysqlPipeline': 302,
    'CNKIPaSearchCrontab.pipelines.JsonPipeline': 303,
}

# 禁止重定向
REDIRECT_ENALBED = False
# 允许出现404 403
HTTPERROR_ALLOWED_CODES = [404, 403, 401]
# 下载限制15秒为延时 默认180s
DOWNLOAD_TIMEOUT = 5

