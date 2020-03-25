# --coding:UTF-8--
from dotenv import load_dotenv
from CNKIPaSearchCrontab.spiders.page import PageSpider
from CNKIPaSearchCrontab.spiders.detail import DetailSpider

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
import time
from CNKIPaSearchCrontab.utils import db
from CNKIPaSearchCrontab.utils.config import *
import os
import json
import sys
import datetime

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging



#
# @defer.inlineCallbacks
# def crawl():
#     load_dotenv()
#     yield runner(PageSpider)
#     yield runner(DetailSpider)
#     reactor.stop()
#
#
# if __name__ == '__main__':
#     configure_logging()
#     runner = CrawlerRunner(get_project_settings())
#     crawl()
#     reactor.run()



def start_spider_page(school):
    # db.create_engine(**DB_CONFIG)
    # 爬取使用的spider名称
    spider_name1 = 'page'
    spider_name2 = 'detail'
    # spider_name = school
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    # 合并配置
    process = CrawlerProcess(settings)
    process.crawl(spider_name1, school=school)
    process.start()


def start_spider_detail():
    # db.create_engine(**DB_CONFIG)
    # 加载.env配置文件
    # load_dotenv()
    # 爬取使用的spider名称
    spider_name = 'detail'
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    # 合并配置
    process = CrawlerProcess(settings)
    # 启动爬虫
    process.crawl(spider_name)
    process.start()


def get_school():
    """

    """
    db.create_engine(**DB_CONFIG)
    sql = "select `NAME` school from es_school where `LEVEL` = '985'"
    res = db.execute(sql)
    print(res)
    with open("./crontab_list.json", 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=4)


def get_file_name():
    """
    获取当前年月
    """
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    current_day = datetime.datetime.now().day
    if current_month < 10:
        current_month = "0" + str(current_month)
    else:
        current_month = str(current_month)
    if current_day > 15:
        year_month = str(current_year) + "_" + current_month + "_down"
    else:
        year_month = str(current_year) + "_" + current_month + "_up"
    return year_month

if __name__ == '__main__':
    # file_name = get_file_name()
    load_dotenv()
    start_spider_page("crontab_list")
    # time.sleep(10)
    # start_spider_detail()

    # get_school()