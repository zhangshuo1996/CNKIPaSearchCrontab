import pymysql.cursors
import datetime
from CNKIPaSearch.utils.logger import logger
from CNKIPaSearch.utils.config import LOG_PATH


class DBhelper(object):
    # 数据库连接配置
    connect = pymysql.connect(
        host = '106.15.188.196',  # 数据库地址
        port = 3306,  # 数据库端口
        db = 'ip_pool',  # 数据库名
        user = 'root',  # 数据库用户名
        passwd = 'chenmeng',  # 数据库密码
        charset = 'utf8',  # 编码方式
        use_unicode = True
    )

    # 通过cursor执行增删查改
    cursor = connect.cursor()
    
    def execute(self,sql,errorMsg="has error"):
        """
        执行 sql 语句
        :param sql:
        :param errorMsg: sql 执行错误的打印值，用于定位 错误地点
        :return:
        """
        try:
            # 执行 sql 语句
            self.cursor.execute(sql)

            """
                data type : ((a1,b1,..),(a2,...),...)
            """
            data = self.cursor.fetchall()

            # 提交 sql 语句
            self.connect.commit()
            
            return data

        except Exception as e:
            logger.error(errorMsg,e)
            log_path = "%s/sql_error.txt" % LOG_PATH
            with open(log_path, "a", encoding="utf8") as f:
                f.write("%s\t%s\t error: %s \t\n sql is %s\n" % (datetime.datetime.now(), errorMsg, e, sql))
            return False


    def get_useful_proxy(self, https = False):
        """
        返回可用的代理，格式为：
        {"ip:port" : score, ... } or None        
        """
        sql = "SELECT ip, port, score FROM ip where score > 3"
        
        if https:
            sql = "SELECT ip, port, score FROM ip where score > 3 and http_type > 1"
        
        proxy = self.execute(sql, errorMsg="获取可用代理失败")

        if not proxy or len(proxy) < 1:
            return None
        
        back_dict = {}
        for item in proxy:
            ip, port, score = item[0], item[1], item[2]
            key = "%s:%s" % (ip, port)
            
            back_dict[key] = score

        return back_dict


    def remove_proxy(self, proxy):
        # proxy  ==>  "171.35.162.35:9999"
        try:
            proxy = proxy.split(":")
            ip, port = proxy[0], int(proxy[1])
            
            sql = "update ip set score=0 where ip='%s' and port=%d" % (ip, port)

            # 更新成功 返回空tuple () , 失败为False
            if self.execute(sql) != False:
                return True
            else:
                logger.warning("移除代理 %s:%s 失败" % (ip, port))
                return False
        except Exception as e:
            logger.warning("降低 %s:%s score 失败, 原因: %s" % (ip, port, e))


if __name__ == "__main__":
    sql = "update ip set score=0 where ip='171.35.162.35' and port=9999"
    back = DBhelper().execute(sql)
    print(back, type(back))
