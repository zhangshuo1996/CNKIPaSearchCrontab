# -*- coding: utf-8 -*-
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
from CNKIPaSearchCrontab.items import PagePatentItem
from CNKIPaSearchCrontab.items import DetailPatentItem
import os
import json
import datetime
import logging
from scrapy.exceptions import DropItem
from CNKIPaSearchCrontab.utils import db
from CNKIPaSearchCrontab.utils.config import *

logger = logging.getLogger(__name__)


def get_cur_year_month():
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


def get_path(spider, path_name):
    year_month = get_cur_year_month()
    basedir = spider.settings.get('BASEDIR')
    # school = list(spider.request_datum.values())[0]
    # teacher = list(spider.request_datum.values())[1]
    school = spider.request_datum["school"]
    # teacher = spider.request_datum["teacher"]
    # variable = re.sub('/', '-', school)
    path = os.path.join(basedir, 'crontab_files', path_name, str(year_month))

    return path


class PageJsonPipeline(object):
    def __init__(self):
        self.filepath = None
        # 数据库中已存在的教师、学校、id的对应关系
        self.teacher_school_id_dict = self.get_existed_teacher_info()

    def process_item(self, item, spider):
        # 如果item类型是detail， 直接返回item
        if isinstance(item, DetailPatentItem):
            return item
        tmp_d = dict(item)
        self.filepath = get_path(spider, 'page_links')
        school_teacher = item["school_teacher"]
        school = school_teacher["school"]
        index = spider.cur_page

        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)

        filename = os.path.join(self.filepath, '%s.json' % school)
        json_data = []
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf8') as fp:
                json_data = json.load(fp)
        json_data.extend(item['array'])
        print(list(json_data))
        with open(filename, "w", encoding='utf-8') as fp:
            fp.write(json.dumps(json_data, ensure_ascii=False, indent=2))

        return item

    def save_teacher_patent(self):
        """
        构建专利与教师之间的关系，存入文件
        """
        for filename in os.listdir(self.filepath):
            self.save_single_teacher_patent(self.filepath, filename)

    def save_single_teacher_patent(self, filepath, filename):
        """
        将单个文件夹下的专利与教师关系保存到当前路径下， 文件名为： school_patent.json
        """
        full_path_name = os.path.join(filepath, filename)
        with open(full_path_name, 'r', encoding='utf8') as fp:
            json_data = json.load(fp)
        teacher_patent_list = []
        for d in json_data:
            patent_id = d["patent_id"]
            publication_number = d["filename"]
            school = d["school"]
            inventor_list = d["inventor"].split(";")

            for inventor in inventor_list:
                if inventor in self.teacher_school_id_dict.keys():
                    if school in self.teacher_school_id_dict[inventor].keys():
                        teacher_id = self.teacher_school_id_dict[inventor][school]
                        teacher_patent_list.append({
                            "teacher_id": teacher_id,
                            "patent_id": patent_id,
                            "publication_number": publication_number
                        })
        write_path = os.path.join(filepath, filename.split(".")[0] + "_patent.json")
        with open(write_path, 'w', encoding='utf8') as fp:
            json.dump(teacher_patent_list, fp, ensure_ascii=False, indent=4)
        logging.info(filename + "关系写入完成")

    def get_existed_teacher_info(self):
        """
        获取已存在的教师信息
        return: {
                    teacher_name: {
                                    school_name: teacher_id,
                                    school_name2: teacher_id2,
                                    ...
                                    },
                                    ...
                }
        """
        sql = """
            select es_teacher.`NAME` teacher, es_teacher.ID teacher_id, es_school.`NAME` school
            from es_teacher LEFT JOIN es_school
            on es_teacher.SCHOOL_ID = es_school.ID
        """
        res = db.execute(sql)
        teacher_school_id_dict = {}
        for d in res:
            teacher = d["teacher"]
            school = d["school"]
            teacher_id = d["teacher_id"]
            if teacher in teacher_school_id_dict.keys():
                temp_dict = teacher_school_id_dict[teacher]
                temp_dict[school] = teacher_id
                teacher_school_id_dict[teacher] = temp_dict
            else:
                teacher_school_id_dict[teacher] = {
                    school: teacher_id
                }
        return teacher_school_id_dict

    def close_spider(self, spider):
        """
        仅仅爬虫page使用
        关闭爬虫前 将新爬取的专利与专利id做好对应
        """
        if spider.name == "detail":
            return
        self.save_teacher_patent()


# ----------------------下面是detail中的item-------------------------------


class FilterPipeline(object):
    """清除特殊字符"""
    def __init__(self):
        # 字符串转为数组
        self.array_keys = ['inventor', 'patent_cls_number', 'agent', 'applicant', 'joint_applicant']
        # TODO:字符串转为datetime
        # self.date_keys = ['application_date', 'publication_date']
        self.date_keys = []
        # 去多个换行
        self.text_keys = ['sovereignty', 'summary']
        self.pattern = re.compile(r'[\n|\r]+')
        # 转成int
        self.int_keys = ['page_number']

    def process_item(self, item, spider):
        # 如果是page对应的item， 不做处理，直接返回item
        if isinstance(item, PagePatentItem):
            return item
        try:
            for key, value in item.items():
                if key in self.array_keys:
                    item[key] = []
                    for v in value.split(';'):
                        if len(v) > 0:
                            item[key].append(v)
                elif key in self.date_keys:
                    item[key] = datetime.datetime.strptime(value, '%Y-%m-%d')
                elif key in self.text_keys:
                    item[key] = re.sub(self.pattern, '', value)
                elif key in self.int_keys:
                    item[key] = int(value)
            if 'response' in item:
                del item['response']
        except Exception as e:
            # 在解析时出现错误，则报错后移除该item
            logger.error('process [%s] error: %s' % (item['publication_number'], e))
            raise DropItem()

        return item


class JsonPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            basedir=crawler.settings.get('BASEDIR'),
        )

    def __init__(self, basedir):
        self.save_path = os.path.join(basedir, 'crontab_files', 'detail')
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def process_item(self, item, spider):
        """
        将专利的具体内容（）写入detail文件
        """
        # 如果是page对应的item， 不做处理，直接返回item
        if isinstance(item, PagePatentItem):
            return item
        school = dict(item)['school']
        if school not in self.save_path:
            save_path = os.path.join(self.save_path, school)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
        # if not os.path.exists(save_path):
        #     os.makedirs(save_path)
        filename = os.path.join(save_path, '%s.json' % item['publication_number'])
        with open(filename, "w", encoding='utf-8') as fp:
            fp.write(json.dumps(dict(item), ensure_ascii=False, indent=2))
        return item


class MysqlPipeline(object):
    """
    将专利的基本信息存入mysql
    将专利的长文本信息存入文件
    """
    def __init__(self, basedir):
        # db.create_engine(**DB_CONFIG)
        self.basedir = basedir
        self.file_buffer = []
        self.mysql_buffer = []
        self.data_length = 0
        self.school = None
        self.year_month = None
        self.error_list = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            basedir=crawler.settings.get('BASEDIR')
        )

    def open_spider(self, spider):
        self.db = db

    def process_item(self, item, spdier):
        # 通过application_number保证唯一
        if spdier.name == "page":
            return item
        print()
        if isinstance(item, PagePatentItem):
            return item
        self.write_file(item)
        self.write_mysql(item)
        return item

    def write_file(self, item):
        """
        将专利id和长文本写入faiss_data
        """
        patent_id = item['patent_id']
        introduction_text = item['summary'] + item['sovereignty']
        school = item["school"]
        self.year_month = item["year_month"]
        self.school = school
        write_dict = {
            "abstract": introduction_text,
            "id": patent_id
        }
        self.file_buffer.append(write_dict)

        # 缓冲区长度 > 40, 将里面的内容写入文件
        if len(self.file_buffer) > 40:
            self.write_to_file()

    def write_to_file(self):
        """
        将缓冲区里的内容：
        [
            {
                patent_id: 专利介绍
            },
            ...
        ]
        写入文件
        """
        json_data = []
        file_path = os.path.join(self.basedir, 'crontab_files', 'faiss_data', self.year_month + '.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf8') as f1:
                json_data = json.load(f1)
        else:
            with open(file_path, 'w', encoding='utf8') as f3:
                json.dump([], f3)
        json_data.extend(self.file_buffer)
        with open(file_path, 'w', encoding='utf8') as f2:
            json.dump(json_data, f2, ensure_ascii=False, indent=4)
        self.file_buffer.clear()  # 清空缓冲区

    def write_mysql(self, item):
        """
        将专利基本信息写入mysql
        """

        self.mysql_buffer.append(dict(item))

        # 每爬取40条专利，插入mysql，并清空缓存
        if len(self.mysql_buffer) > 40:
            self.insert_into_mysql()
            self.mysql_buffer.clear()

    def insert_into_mysql(self):
        """
        将多条专利的基本信息插入mysql（具体插入代码）
        """
        sql = "insert into patent3(`id`, title, publication_number, publication_year," \
              "applicant, address, inventor, code, page_number, main_cls_number, patent_cls_number" \
              ") values"
        for d in self.mysql_buffer:
            print("显示字典", d)
            if "page_number" not in d.keys():
                self.error_list.append(d['patent_id'])
                continue
            sql += "(" + str(d['patent_id']) + ", \"" + d['title'] + "\", \"" + \
                   d['publication_number'] + "\", \"" + d["publication_date"] + "\", \"" + str(d['applicant']) + \
                   "\", \"" + d['address'] + "\", \"" + str(d["inventor"]) + "\", \"" + d["code"] + "\", \"" + \
                   str(d["page_number"]) + "\", \"" + d["main_cls_number"] + "\", \"" + str(d["patent_cls_number"]) + "\"),"
        sql = sql[0:-1]
        print(sql)
        if sql[-1] != ")":
            return
        try:
            # self.db.my_insert(sql)
            self.data_length += len(self.mysql_buffer)
            print("______________________________________插入成功")
        except Exception as e:
            print("数据插入失败：  ", e)

    def close_spider(self, spider):
        """
        关闭爬虫前， 将缓冲区内的内容写入文件和mysql， 并记录错误信息
        """
        # 爬虫是page，则跳过
        if spider.name == "page" or self.year_month is None:
            return

        # 缓冲区内的剩余内容写入文件
        if len(self.file_buffer) > 0:
            self.write_to_file()

        # 缓冲区内的剩余内容写入mysql
        if len(self.mysql_buffer) > 0:
            self.insert_into_mysql()

        # 将爬取失败的写入文件
        error_path = os.path.join(self.basedir, 'crontab_files', 'error', self.year_month + "error.json")
        with open(error_path, 'w', encoding='utf8') as f:
            json.dump(self.error_list, f)


