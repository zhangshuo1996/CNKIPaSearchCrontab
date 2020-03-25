# -*- coding: utf-8 -*-
# Define here the models for your spider middleware
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
print(os.getcwd())
os.chdir(os.getcwd())
import json
import logging
import requests
from twisted.internet.error import TimeoutError
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from CNKIPaSearchCrontab.hownet_config import *
from CNKIPaSearchCrontab.config import PROXY_URL
import time
import datetime
import calendar
import random
from scrapy.http import HtmlResponse



logger = logging.getLogger(__name__)


def get_random_proxy3():
    """获取随机的IP代理 by 购买"""
    time.sleep(0.5)
    # PROXY_URL = PROXY_URL
    response = requests.get(PROXY_URL, timeout=5)
    # datum = json.load(response.text)
    text = response.text
    try:
        print(text)
        datum = eval(text)
        print(datum)
        return datum['data'][0]['IP']
    except:
        time.sleep(1)
        print("购买的代理出错, 正在重试------------ ")
        return get_random_proxy3()


class GetFromLocalityMiddleware(object):
    def process_request(self, request, spider):
        """
        尝试从本地获取源文件，如果存在，则直接获取
        :param request:
        :param spider:
        :return:
        """
        # 如果爬虫是page， 则跳过
        if spider.name == "page":
            return
        # 提取出code
        filename = request.meta['publication_number']
        # 文件存放位置
        path = request.meta['path']
        # 该路径存在该文件
        filepath = os.path.join(path, '%s.html' % filename)
        if os.path.exists(filepath):
            fp = open(filepath, 'rb')
            body = fp.read()
            fp.close()
            # 从本地加载的文件不再重新写入
            request.meta['load_from_local'] = True
            return HtmlResponse(url=request.url, headers=request.headers, body=body, request=request)
        return None


def date2str(date):
    date_string = date.strftime('%Y-%m-%d')
    return date_string


class RetryOrErrorMiddleware(RetryMiddleware):
    """在之前的基础上增加了一条判断语句，当重试次数超过阈值时，发出错误"""

    def _retry(self, request, reason, spider):
        # 获取当前的重试次数
        retry_times = request.meta.get('retry_times', 0) + 1
        # 最大重试次数
        max_retry_times = self.max_retry_times
        if 'max_retry_times' in request.meta:
            max_retry_times = request.meta['max_retry_times']

        # 超出重试次数
        if retry_times > max_retry_times:
            datum = spider.request_error()
            logger.error('%s %s retry times beyond the bounds' % (request.url, datum))
        super()._retry(request, reason, spider)

    def process_exception(self, request, exception, spider):
        # 出现超时错误时，再次请求
        if isinstance(exception, TimeoutError):
            return request


class ProxyMiddleware(object):
    def __init__(self):
        self.proxy = None
        self.pre_time = None
        self.ip_list = []

    def fill_ip_list(self):
        """
        重新替换ip_list中的ip
        """
        self.ip_list = []
        i = 0
        while i < 3:
            i += 1
            self.ip_list.append(self.get_random_proxy3())
            time.sleep(1)

    def get_random_proxy3(self):
        """获取随机的IP代理 by 购买"""
        time.sleep(0.5)
        # PROXY_URL = PROXY_URL
        response = requests.get(PROXY_URL, timeout=5)
        # datum = json.load(response.text)
        text = response.text
        try:
            print(text)
            datum = eval(text)
            print(datum)
            return datum['data'][0]['IP']
        except:
            time.sleep(1)
            print("购买的代理出错, 正在重试------------ ")
            return self.get_random_proxy3()

    def process_request(self, request, spider):
        # 最大重试次数
        retry_times = request.meta.get('retry_times', 0)
        max_retry_times = spider.crawler.settings.get('MAX_RETRY_TIMES')
        if len(self.ip_list) == 0:
            self.fill_ip_list()
            self.pre_time = time.time()
        else:
            cur_time = time.time()
            pass_time = int(cur_time - self.pre_time)
            if pass_time > 40:
                self.pre_time = time.time()
                self.fill_ip_list()
        self.proxy = random.choice(self.ip_list)
        # 最后一次尝试不使用代理
        if self.proxy and retry_times != max_retry_times:
            logger.info('使用代理%s' % self.proxy)
            request.meta['proxy'] = 'http://%s' % self.proxy
        else:
            reason = '代理获取失败' if self.proxy else ('达到最大重试次数[%d/%d]' % (retry_times, max_retry_times))
            logger.warning('%s，使用自己的IP' % reason)


class CookieMiddleware(object):
    def __init__(self):
        # 使用哪个类作为配置文件
        name = os.getenv('CONFIG', 'KeyWordConfig')
        self.config = configurations[name]
        self.proxy = None
        self.pre_time = None
        self.ip_list = []

    def fill_ip_list(self):
        """
        重新替换ip_list中的ip
        """
        self.ip_list = []
        i = 0
        while i < 1:
            i += 1
            self.ip_list.append(self.get_random_proxy3())
            time.sleep(1)

    def get_random_proxy3(self):
        """获取随机的IP代理 by 购买"""
        time.sleep(0.5)
        # PROXY_URL = PROXY_URL
        response = requests.get(PROXY_URL, timeout=5)
        # datum = json.load(response.text)
        text = response.text
        try:
            print(text)
            datum = eval(text)
            print(datum)
            return datum['data'][0]['IP']
        except:
            time.sleep(1)
            print("购买的代理出错, 正在重试------------ ")
            return self.get_random_proxy3()

    def process_request(self, request, spider):

        # 如果spider是detail， 则不使用cookie
        if spider.name == "detail":
            return

        # 为spider.request_datum 加上参数start_date, end_date
        start_date, end_date = self.get_cur_start_end_date()
        spider.request_datum["start_date"] = start_date
        spider.request_datum["end_date"] = end_date

        # 重新请求cookie
        if spider.cookie_dirty:
            # 死循环获取cookie
            cookie = None
            while not cookie:
                if len(self.ip_list) == 0:
                    self.fill_ip_list()
                    self.pre_time = time.time()
                else:
                    cur_time = time.time()
                    pass_time = int(cur_time - self.pre_time)
                    if pass_time > 60:
                        self.pre_time = time.time()
                        self.fill_ip_list()
                self.proxy = random.choice(self.ip_list)
                proxies = {'http': self.proxy}
                # 根据条件获取cookie
                cookie = self.get_cookie(spider.request_datum, proxies)
                logger.warning('获取cookie %s' % cookie)
            spider.cookie = cookie
        # 赋值cookie
        request.headers['Cookie'] = spider.cookie

    def get_cookie(self, values, proxies=None, **kwargs):
        """
        根据条件给知网发送post请求来获取对应的cookie
        :param values: dict类型的变量
        :param proxies: 代理 proxies = {'http': 'host:port', 'https': 'host:port'}
        :return: cookie 字符串类型，主要用于赋值到header中的Cookie键
        headers = {'Cookie': cookie}
        """
        params = self.config.get_params(**values)
        params.update(**kwargs)
        url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx'
        try:
            response = requests.post(url, params=params, proxies=proxies, timeout=5)
            cookies = requests.utils.dict_from_cookiejar(response.cookies)

            cookie_str = ""
            for key in cookies:
                value = cookies[key]
                text = "%s=%s;" % (key, value)
                cookie_str += text
            return cookie_str

        except Exception as e:
            logger.warning('cookie获取失败')
        return None

    def get_cur_start_end_date(self):
        """
        获取以当前时间的为准的开始与结束时间：
        例如当前时间是2020-3-23 ， 则返回2020-3-16， 2020-3-31
           当前时间是2020-3-12，   则返回2020-3-1， 2020-3-15
        """
        cur_year = datetime.datetime.now().year
        cur_month = datetime.datetime.now().month

        cur_day = datetime.datetime.now().day
        if cur_day > 16:
            days = calendar.monthrange(cur_year, cur_month)  # 获取当前月份有几天
            if cur_month < 10:
                cur_month = "0" + str(cur_month)
            start_date = str(cur_year) + "-" + cur_month + "-" + str(16)
            end_date = str(cur_year) + "-" + cur_month + "-" + str(days[1])
        else:
            if cur_month < 10:
                cur_month = "0" + str(cur_month)
            start_date = str(cur_year) + "-" + cur_month + "-" + str(1)
            end_date = str(cur_year) + "-" + cur_month + "-" + str(15)
        # print(start_date, "    ", end_date)
        start_date = "2020-03-01"
        end_date = "2020-03-07"
        return start_date, end_date


