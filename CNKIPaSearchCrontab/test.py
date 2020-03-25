# import urllib3, urllib

from urllib.parse import unquote
"""
https://kns.cnki.net/kns/brief/brief.aspx?
pagename=ASP.brief_result_aspx&
isinEn=0&
dbPrefix=SCOD&
dbCatalog=%e4%b8%93%e5%88%a9%e6%95%b0%e6%8d%ae%e6%80%bb%e5%ba%93&
ConfigFile=SCOD.xml&
research=off&
t=1583822197504&
keyValue=%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6&
S=1&
sorttype=
"""
import datetime
import calendar

def get_time():
    cur_year = datetime.datetime.now().year
    cur_month = datetime.datetime.now().month
    cur_day = datetime.datetime.now().day
    if cur_day > 16:
        days = calendar.monthrange(cur_year, cur_month)  # 获取当前月份有几天
        start_date = str(cur_year) + "-" + str(cur_month) + "-" + str(16)
        end_date = str(cur_year) + "-" + str(cur_month) + "-" + str(days[1])
    else:
        start_date = str(cur_year) + "-" + str(cur_month) + "-" + str(1)
        end_date = str(cur_year) + "-" + str(cur_month) + "-" + str(15)
    # print(start_date, "    ", end_date)
    return start_date, end_date



if __name__ == '__main__':
    # s1 = "%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6"
    # s2 = "%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6"
    # print(unquote(s2))
    get_time()
