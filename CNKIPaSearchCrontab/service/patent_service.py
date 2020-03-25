import random
from CNKIPaSearchCrontab.utils.db import *
from CNKIPaSearchCrontab.utils.config import DB_CONFIG


def get_existed_patent():
    """
    获取数据库中已经存在的专利信息
    return: {
            专利公开号：patent_id,
            ..,
            ..
            }
    """
    sql = "select publication_number filename, id patent_id from patent3"
    res = execute(sql)
    exist_patent_dict = {}
    for tup in res:
        exist_patent_dict[tup["filename"]] = tup["patent_id"]
    print(exist_patent_dict)
    return exist_patent_dict


def generate_random_patent_id():
    """
    生成随机的10位专利id
    return: patent_id
    """
    res = [{}]
    while len(res) > 0:
        try:
            rand = generate_random()
            sql = "select id from patent where id = " + str(rand)
            res = execute(sql)
            if len(res) == 0:
                return rand
        except:
            print("get random id error")


def generate_random():
    """
    生成10位随机数
    """

    return int("".join(random.choice("0123456789") for i in range(10)))


if __name__ == '__main__':

    # 需要预先调用，且只调用一次
    create_engine(**DB_CONFIG)
    # get_existed_patent()
    r = generate_random_patent_id()
    print(r)