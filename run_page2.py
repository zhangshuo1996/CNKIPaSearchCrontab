import time
import os


if __name__ == '__main__':
    os.system("scrapy crawl page -a school=crontab_list")
    time.sleep(30)
    os.system("scrapy crawl detail")