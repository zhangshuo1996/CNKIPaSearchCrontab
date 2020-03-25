"""
ip池管理
"""

import random
import datetime
from CNKIPaSearchCrontab.utils.logger import logger
from CNKIPaSearchCrontab.utils.dbhelper import DBhelper


class Proxies(object):

    def __init__(self, https=False):
        # 用于保存返回的ip代理, 格式为：
        # {"http://ip:port" : score, ... }
        self.proxies_pool = {}

        self.DB = DBhelper()

        self.https = https
        self.__get_proxy_from_DB()
    

    def istime2update(self):
        """
        设定每天凌晨4点更新一次 sum_usefulIp
        原因在于每天凌晨3点开始更新+检验IP池
        """
        now_time = datetime.datetime.now()

        # if now_time.hour == 4 and now_time.minute == 0 and now_time.second == 0:
        # 每20min更新一次
        if now_time.minute % 20 == 0:
            return True
        return False


    def __get_proxy_from_DB(self):
        """
        从数据库中获取可用代理
        """

        self.proxies_pool = self.DB.get_useful_proxy(https = self.https)

        if self.proxies_pool is None:
            logger.error("获取ip失败")
            return False

        logger.info("重获ip池，共%s条可用" % len(self.proxies_pool))
        
        return True


    def __get_one_proxy(self):
        """
        随机返回一个可用代理
        """
        return random.choice(list(self.proxies_pool.keys()))


    def getProxy(self):
        """
        根据参数 https 返回代理，格式为：
        "http(s)://ip:port" or False
        """
        if len(self.proxies_pool) == 0 or self.istime2update():
            self.__get_proxy_from_DB()
        
        if not self.proxies_pool or len(self.proxies_pool) == 0:
            # ip池耗尽
            # logger.error("ip池耗尽")
            # return False
            return "ip池耗尽"
            
        proxy = self.__get_one_proxy()
        
        # if self.https:
        #     proxy = "https://%s" % proxy
        # else:
        #     proxy = "http://%s" % proxy

        # logger.info("当前ip:%s ,尚有%s条可用" % (proxy, len(self.proxies_pool)))

        return proxy


    def getAllProxy(self):
        """
        根据参数 https 返回代理，格式为：
         {"ip:port":score,...] or False
        """
        if len(self.proxies_pool) == 0 or self.istime2update():
            self.__get_proxy_from_DB()

        if len(self.proxies_pool) == 0:
            # ip池耗尽
            # logger.error("ip池耗尽")
            # return False
            return "ip池耗尽"

        # if self.https:
        #    proxy = ["https://%s,%s" % (proxy, score) for proxy, score in self.proxies_pool.items()]
        #else:
        #    proxy = ["http://%s,%s" % (proxy, score) for proxy, score in self.proxies_pool.items()]
        
        #return proxy
        return self.proxies_pool

        

    def decrease_score(self, proxy):
        """
        降低代理评分
            proxy  ==>  "https://171.35.162.35:9999"
        return: None
        """
        try:
            proxy = proxy.split("//")[1]
            score = self.proxies_pool[proxy] - 1

            if score > 0:
                self.proxies_pool[proxy] = score
                logger.info("代理 %s 评分降至 %s" % (proxy, score))
            else:
                self.DB.remove_proxy(proxy)

                logger.info("移除代理 %s, 尚有%d条代理可用" % (proxy, len(self.proxies_pool)))

        except Exception as e:
            logger.error("代理%s不在IP池中： %s" % (proxy, e))

    
if __name__ == "__main__":
    proxy = Proxies(https=True)
    tp = proxy.getProxy()
    print("----------")
    print(tp)
    print("----------")
    # proxy.decrease_score(tp)

    
