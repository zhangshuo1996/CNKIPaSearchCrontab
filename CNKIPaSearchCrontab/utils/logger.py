import logging
import datetime
import os
from logging import handlers
from CNKIPaSearch.utils.config import LOG_PATH


class Logger(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        #设置日志输出格式
        format_str = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

        #设置日志级别
        self.logger.setLevel(logging.INFO)
        
        #往屏幕上输出
        sh = logging.StreamHandler()
        #设置屏幕上显示的格式
        sh.setFormatter(format_str)

        if not os.path.exists(LOG_PATH):
            os.mkdir(LOG_PATH)

        # xxx/logs/2019-9-5.txt
        filename = "%s/%s.txt" % (LOG_PATH, datetime.date.today())
        """
            往文件里写入指定间隔时间自动生成文件的处理器
            实例化TimedRotatingFileHandler
            interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
            S 秒
            M 分
            H 小时、
            D 天、
            W 每星期（interval==0时代表星期一）
            midnight 每天凌晨
        """
        th = handlers.TimedRotatingFileHandler(filename=filename, when= "D", backupCount=3, encoding='utf-8')
        #设置文件里写入的格式
        th.setFormatter(format_str)
        #把对象加到logger里
        self.logger.addHandler(sh)
        self.logger.addHandler(th)

    def getLogger(self):
        return self.logger


logger = Logger().getLogger()


if __name__ == '__main__':
    logger = Logger().getLogger()
    logger.debug('debug')
    logger.info('info')
    logger.warning('警告')
    logger.error('报错')
    logger.critical('严重')
