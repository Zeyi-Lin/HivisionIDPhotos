import os
import pymongo
import datetime
import time
from .cloudService import GetConfig
local_path = os.path.dirname(__file__)


class DBUtils(GetConfig):
    """
    从安全的角度出发,将一些默认配置文件上传至COS中,接下来使用COS和它的子类的时候,在第一次使用时需要输入Cuny给的id和key
    用于连接数据库等对象
    当然,在db_default_download = False的时候,如果在运行路径下已经有配置文件了,
    那么就不用再次下载了,也不用输入id和key
    事实上这只需要运行一次,因为配置文件将会被下载至源码文件夹中
    如果要自定义路径,请在继承的子类中编写__init__函数,将service_path定向到指定路径
    """
    __BASE_DIR: dict = None
    __PARAMS_DIR: dict = None
    db_base_path: str = f"{local_path}/conf/base_config.json"
    db_params_path: str = f"{local_path}/conf/params.json"
    db_default_download: bool = False

    @property
    def base_config(self):
        if self.__BASE_DIR is None:
            self.__BASE_DIR = self.load_json(self.db_base_path, self.db_default_download)
        return self.__BASE_DIR

    @property
    def db_config(self):
        return self.base_config["database_config"]

    @property
    def params_config(self):
        if self.__PARAMS_DIR is None:
            self.__PARAMS_DIR = self.load_json(self.db_params_path, self.db_default_download)
        return self.__PARAMS_DIR

    @property
    def size_dir(self):
        return self.params_config["size_config"]

    @property
    def func_dir(self):
        return self.params_config["func_config"]

    @property
    def wx_config(self):
        return self.base_config["wx_config"]

    def get_dbClient(self):
        return pymongo.MongoClient(self.db_config["connect_url"])

    @staticmethod
    def get_time(yyyymmdd=None, delta_date=0):
        """
        给出当前的时间
        :param yyyymmdd: 以yyyymmdd给出的日期时间
        :param delta_date: 获取减去delta_day后的时间，默认为0就是当天
        时间格式:yyyy_mm_dd
        """
        if yyyymmdd is None:
            now_time = (datetime.datetime.now() - datetime.timedelta(delta_date)).strftime("%Y-%m-%d")
            return now_time
        # 输入了yyyymmdd的数据和delta_date,通过这两个数据返回距离yyyymmdd   delta_date天的时间
        pre_time = datetime.datetime(int(yyyymmdd[0:4]), int(yyyymmdd[4:6]), int(yyyymmdd[6:8]))
        return (pre_time - datetime.timedelta(delta_date)).strftime("%Y-%m-%d")

    # 获得时间戳
    def get_timestamp(self, date_time:str=None) -> int:
        """
        输入的日期形式为:"2021-11-29 16:39:45.999"
        真正必须输入的是前十个字符,及精确到日期,后面的时间可以不输入,不输入则默认置零
        """
        def standardDateTime(dt:str) -> str:
            """
            规范化时间字符串
            """
            if len(dt) < 10:
                raise ValueError("你必须至少输入准确到天的日期!比如:2021-11-29")
            elif len(dt) == 10:
                return dt + " 00:00:00.0"
            else:
                try:
                    date, time = dt.split(" ")
                except ValueError:
                    raise ValueError("你只能也必须在日期与具体时间之间增加一个空格,其他地方不能出现空格!")
                while len(time) < 10:
                    if len(time) in (2, 5):
                        time += ":"
                    elif len(time) == 8:
                        time += "."
                    else:
                        time += "0"
                return date + " " + time
        if date_time is None:
            # 默认返回当前时间(str), date_time精确到毫秒
            date_time = datetime.datetime.now()
        # 转换成时间戳
        else:
            date_time = standardDateTime(dt=date_time)
            date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S.%f")
        timestamp_ms = int(time.mktime(date_time.timetuple()) * 1000.0 + date_time.microsecond / 1000.0)
        return timestamp_ms

    @staticmethod
    def get_standardTime(yyyy_mm_dd: str):
        return yyyy_mm_dd[0:4] + yyyy_mm_dd[5:7] + yyyy_mm_dd[8:10]

    def find_oneDay_data(self, db_name: str, collection_name: str, date: str = None) -> dict:
        """
        获取指定天数的数据，如果date is None，就自动寻找距今最近的有数据的那一天的数据
        """
        df = None  # 应该被返回的数据
        collection = self.get_dbClient()[db_name][collection_name]
        if date is None:  # 自动寻找前几天的数据,最多三十天
            for delta_date in range(1, 31):
                date_yyyymmdd = self.get_standardTime(self.get_time(delta_date=delta_date))
                filter_ = {"date": date_yyyymmdd}
                df = collection.find_one(filter=filter_)
                if df is not None:
                    del df["_id"]
                    break
        else:
            filter_ = {"date": date}
            df = collection.find_one(filter=filter_)
            if df is not None:
                del df["_id"]
        return df

    def find_daysData_byPeriod(self, date_period: tuple, db_name: str, col_name: str):
        # 给出一个指定的范围日期，返回相应的数据(日期的两头都会被寻找)
        # 这个函数我们默认数据库中的数据是连续的，即不会出现在 20211221 到 20211229 之间有一天没有数据的情况
        if len(date_period) != 2:
            raise ValueError("date_period数据结构：(开始日期，截止日期)")
        start, end = date_period  # yyyymmdd
        delta_date = int(end) - int(start)
        if delta_date < 0:
            raise ValueError("传入的日期有误！")
        collection = self.get_dbClient()[db_name][col_name]
        date = start
        while int(date) <= int(end):
            yield collection.find_one(filter={"date": date})
            date = self.get_standardTime(self.get_time(date, -1))

    @staticmethod
    def find_biggest_valueDict(dict_: dict):
        # 寻找字典中数值最大的字段，要求输入的字典的字段值全为数字
        while len(dict_) > 0:
            max_value = 0
            p = None
            for key in dict_:
                if dict_[key] > max_value:
                    p = key
                    max_value = dict_[key]
            yield p, max_value
            del dict_[p]

    def copy_andAdd_dict(self, dict_base, dict_):
        # 深度拷贝字典，将后者赋值给前者
        # 如果后者的键名在前者已经存在，则直接相加。这就要求两者的数据是数值型
        for key in dict_:
            if key not in dict_base:
                dict_base[key] = dict_[key]
            else:
                if isinstance(dict_[key], int) or isinstance(dict_[key], float):
                    dict_base[key] = round(dict_[key] + dict_base[key], 2)
                else:
                    dict_base[key] = self.copy_andAdd_dict(dict_base[key], dict_[key])
        return dict_base

    @staticmethod
    def compare_data(dict1: dict, dict2: dict, suffix: str, save: int, **kwargs):
        """
        有两个字典,并且通过kwargs会传输一个新的字典,根据字典中的键值我们进行比对,处理成相应的数据格式
        并且在dict1中,生成一个新的键值,为kwargs中的元素+suffix
        save:保留几位小数
        """
        new_dict = dict1.copy()
        for key in kwargs:
            try:
                if kwargs[key] not in dict2 or int(dict2[kwargs[key]]) == -1 or float(dict1[kwargs[key]]) <= 0.0:
                    # 数据不存在
                    data_new = 5002
                else:
                    try:
                        data_new = round(
                            ((float(dict1[kwargs[key]]) - float(dict2[kwargs[key]])) / float(dict2[kwargs[key]])) * 100
                            , save)
                    except ZeroDivisionError:
                        data_new = 5002
                    if data_new == 0.0:
                        data_new = 0
            except TypeError as e:
                print(e)
                data_new = 5002  # 如果没有之前的数据,默认返回0
            new_dict[kwargs[key] + suffix] = data_new
        return new_dict

    @staticmethod
    def sum_dictList_byKey(dictList: list, **kwargs) -> dict:
        """
        有一个列表,列表中的元素为字典,并且所有字典都有一个键值为key的字段,字段值为数字
        我们将每一个字典的key字段提取后相加,得到该字段值之和.
        """
        sum_num = {}
        if kwargs is None:
            raise ImportError("Please input at least ONE key")
        for key in kwargs:
            sum_num[kwargs[key]] = 0
        for dict_ in dictList:
            if not isinstance(dict_, dict):
                raise TypeError("object is not DICT!")
            for key in kwargs:
                sum_num[kwargs[key]] += dict_[kwargs[key]]
        return sum_num

    @staticmethod
    def sum_2ListDict(list_dict1: list, list_dict2: list, key_name, data_name):
        """
        有两个列表,列表内的元素为字典,我们根据key所对应的键值寻找列表中键值相同的两个元素,将他们的data对应的键值相加
        生成新的列表字典(其余键值被删除)
        key仅在一个列表中存在,则直接加入新的列表字典
        """
        sum_list = []

        def find_sameKey(kn, key_, ld: list) -> int:
            for dic_ in ld:
                if dic_[kn] == key_:
                    post_ = ld.index(dic_)
                    return post_
            return -1

        for dic in list_dict1:
            key = dic[key_name]  # 键名
            post = find_sameKey(key_name, key, list_dict2)  # 在list2中寻找相同的位置
            data = dic[data_name] + list_dict2[post][data_name] if post != -1 else dic[data_name]
            sum_list.append({key_name: key, data_name: data})
        return sum_list

    @staticmethod
    def find_biggest_dictList(dictList: list, key: str = "key", data: str = "value"):
        """
        有一个列表，里面每一个元素都是一个字典
        这些字典有一些共通性质，那就是里面都有一个key键名和一个data键名，后者的键值必须是数字
        我们根据data键值的大小进行生成，每一次返回列表中data键值最大的数和它的key键值
        """
        while len(dictList) > 0:
            point = 0
            biggest_num = int(dictList[0][data])
            biggest_key = dictList[0][key]
            for i in range(len(dictList)):
                num = int(dictList[i][data])
                if num > biggest_num:
                    point = i
                    biggest_num = int(dictList[i][data])
                    biggest_key = dictList[i][key]
            yield str(biggest_key), biggest_num
            del dictList[point]

    def get_share_data(self, date_yyyymmdd: str):
        # 获得用户界面情况
        visitPage = self.find_oneDay_data(date=date_yyyymmdd,
                                          db_name="cuny-user-analysis",
                                          collection_name="daily-userVisitPage")
        if visitPage is not None:
            # 这一部分没有得到数据是可以容忍的.不用抛出模态框错误
            # 获得昨日用户分享情况
            sum_num = self.sum_dictList_byKey(dictList=visitPage["data_list"],
                                              key1="page_share_pv",
                                              key2="page_share_uv")
        else:
            # 此时将分享次数等置为-1
            sum_num = {"page_share_pv": -1, "page_share_uv": -1}
        return sum_num

    @staticmethod
    def compare_date(date1_yyyymmdd: str, date2_yyyymmdd: str):
        # 如果date1是date2的昨天，那么就返回True
        date1 = int(date1_yyyymmdd)
        date2 = int(date2_yyyymmdd)
        return True if date2 - date1 == 1 else False

    def change_time(self, date_yyyymmdd: str, mode: int):
        # 将yyyymmdd的数据分开为相应的数据形式
        if mode == 1:
            if self.compare_date(date_yyyymmdd, self.get_standardTime(self.get_time(delta_date=0))) is False:
                return date_yyyymmdd[0:4] + "年" + date_yyyymmdd[4:6] + "月" + date_yyyymmdd[6:8] + "日"
            else:
                return "昨日"
        elif mode == 2:
            date = date_yyyymmdd[0:4] + "." + date_yyyymmdd[4:6] + "." + date_yyyymmdd[6:8]
            if self.compare_date(date_yyyymmdd, self.get_standardTime(self.get_time(delta_date=0))) is True:
                return date + "~" + date + " | 昨日"
            else:
                return date + "~" + date

    @staticmethod
    def changeList_dict2List_list(dl: list, order: list):
        """
        列表内是一个个字典,本函数将字典拆解,以order的形式排列键值为列表
        考虑到一些格式的问题,这里我采用生成器的形式封装
        """
        for dic in dl:
            # dic是列表内的字典元素
            tmp = []
            for key_name in order:
                key = dic[key_name]
                tmp.append(key)
            yield tmp

    def dict_mapping(self, dict_name: str, id_: str):
        """
        进行字典映射，输入字典名称和键名，返回具体的键值
        如果不存在，则原路返回键名
        """
        try:
            return getattr(self, dict_name)[id_]
        except KeyError:
            return id_
        except AttributeError:
            print(f"[WARNING]: 本对象内部不存在{dict_name}!")
            return id_

    @staticmethod
    def dictAddKey(dic: dict, dic_tmp: dict, **kwargs):
        """
        往字典中加入参数，可迭代
        """
        for key in kwargs:
            dic[key] = dic_tmp[key]
        return dic


if __name__ == "__main__":
    dbu = DBUtils()