# -*- coding: utf-8 -*-
# !/usr/bin/env python


import pandas as pd
import sys

from config import GetConfig
from util import singleton, convert_time_format, parse_limit, print_summary_information
from data_analysis import DataAnalysisMethod


__author__ = 'berniey'


# @singleton
class DataCore(object):

    def __init__(self, data=None, chunksize=10000000):
        # one size of chunk
        self.chunk_size = chunksize
        self.chunks = []
        self.data = data
        self.files = self._get_files()

    def generate_data(self, is_qiniu='True'):
        self._get_chunks()
        if (self.chunks or self.data) or isinstance(self.data, pd.core.frame.DataFrame):
            self.data = self._aggregate_data(self.chunks)
            if is_qiniu != 'f':
                self._change_data(self.data)
            self.chunks = []
            return self.data

    def get_url_traffic(self, *args, **kwargs):
        return self._set_url_traffic_data(*args, **kwargs)

    def get_url_count(self, *args, **kwargs):
        return self._set_url_count_data(*args, **kwargs)

    def get_ip_traffic(self, *args, **kwargs):
        return self._set_ip_traffic_data(*args, **kwargs)

    def get_ip_count(self, *args, **kwargs):
        return self._set_ip_count_data(*args, **kwargs)

    def get_code_count(self, *args, **kwargs):
        return self._set_code_count(*args, **kwargs)

    def get_ip_url_code_count(self, *args, **kwargs):
        return self._set_ip_url_code_count(*args, **kwargs)

    def get_url_code_count(self, *args, **kwargs):
        return self._set_url_code_count(*args, **kwargs)

    def get_ip_code_count(self, *args, **kwargs):
        return self._set_ip_code_count(*args, **kwargs)

    def get_time_traffic(self, *args, **kwargs):
        return self._set_time_traffic(*args, **kwargs)

    def get_time_count(self, *args, **kwargs):
        return self._set_time_count(*args, **kwargs)

    def get_data_by_factor(self, *args, **kwargs):
        return self._set_data_by_factor(*args, **kwargs)

    def _set_url_traffic_data(self, *args, **kwargs):
        return DataAnalysisMethod.url_traffic(self.data, *args, **kwargs)

    def _set_url_count_data(self, *args, **kwargs):
        return DataAnalysisMethod.url_count(self.data, *args, **kwargs)

    def _set_ip_traffic_data(self, *args, **kwargs):
        return DataAnalysisMethod.ip_traffic(self.data, *args, **kwargs)

    def _set_ip_count_data(self, *args, **kwargs):
        return DataAnalysisMethod.ip_count(self.data, *args, **kwargs)

    def _set_code_count(self, *args, **kwargs):
        return DataAnalysisMethod.code_count(self.data, *args, **kwargs)

    def _set_ip_url_code_count(self, *args, **kwargs):
        return DataAnalysisMethod.ip_url_code_count(self.data, *args, **kwargs)

    def _set_url_code_count(self, *args, **kwargs):
        return DataAnalysisMethod.url_code_count(self.data, *args, **kwargs)

    def _set_ip_code_count(self, *args, **kwargs):
        return DataAnalysisMethod.ip_code_count(self.data, *args, **kwargs)

    def _set_time_traffic(self, *args, **kwargs):
        return DataAnalysisMethod.time_traffic(self.data, *args, **kwargs)

    def _set_time_count(self, *args, **kwargs):
        return DataAnalysisMethod.time_count(self.data, *args, **kwargs)

    def _set_data_by_factor(self, *args, **kwargs):
        return DataAnalysisMethod.data_by_factor(self.data, *args, **kwargs)

    def _get_files(self):
        return GetConfig().get_log()

    def _get_chunks(self):
        if not self.files:
            raise Exception("未配置文件")
        for file in self.files:
            self._get_chunk_from_log(file)

    def _get_chunk_from_log(self, log):
        reader = pd.read_csv(log, sep='\s+', names=[i for i in range(10)], iterator=True)
        loop = True
        while loop:
            try:
                chunk = reader.get_chunk(self.chunk_size)
                self.chunks.append(chunk)
            except StopIteration:
                # Iteration is stopped.
                loop = False

    def _aggregate_data(self, chunks):
        return pd.concat(chunks, ignore_index=True)

    def _change_data(self, data):
        # 将3列与4列合并为3列
        data[3] = data[3] + data[4]
        d_time = pd.DataFrame(data[5].str.split(' ').tolist())
        # 删除4，5列
        data.drop([4, 5], axis=1, inplace=True)

        # 将d_time[0]的第一列插入data第四列，并命名为z
        data.insert(4, 'z', d_time[0])
        data.insert(5, 'y', d_time[1])
        data.insert(6, 'x', d_time[2])
        pr_data = pd.DataFrame(data)

        # 重命名整个数据
        pr_data.rename(columns={0: "ip", 1: "hit", 2: 'response_time', 3: 'request_time', 'z': 'method',
                           'y': 'url', 'x': 'Protocol', 6: 'StatusCode', 7: 'TrafficSize',
                           8: 'referer', 9: 'UserAgent'}, inplace=True)

        # 将request_time转为北京时间标准格式
        pr_data['request_time'] = pr_data['request_time'].apply(convert_time_format)
        self.data = pr_data


if __name__ == '__main__':

    pd.set_option('display.max_colwidth', 1000)
    import time
    a = time.time()
    d = DataCore()
    d.generate_data()
    b = time.time()
    print("--日志行数--")
    print(d.data.shape[0])
    num = 20
    if sys.argv[1] == '-s':
        if sys.argv[2:]:
            num = int(sys.argv[2])
            print_summary_information(d, num)

    if sys.argv[1] == '-d':

        print("\n")
        print("指定url {} 的日志如下".format(sys.argv[2]))
        print("\n")
        aim_data = d.get_data_by_factor(limit=(0, 0), url=sys.argv[2])
        print(aim_data.to_string())
        print("\nurl总访问次数如下")
        print(DataCore(aim_data).get_url_count(limit=(0, 0)).to_string())
        print("\nurl总流量如下")
        print(DataCore(aim_data).get_url_traffic(limit=(0, 0)).to_string())
        print("\nurl各个状态码的访问次数如下")
        print(DataCore(aim_data).get_url_code_count(limit=(0, 0)).to_string())

    if sys.argv[1] == '-i':
        print("\n")
        print("指定ip {} 的日志如下".format(sys.argv[2]))
        print("\n")
        aim_data = d.get_data_by_factor(limit=(0, 0), ip=sys.argv[2])
        print(aim_data.to_string())
        print("\nip {} 总访问次数如下".format(sys.argv[2]))
        print(DataCore(aim_data).get_ip_count(limit=(0, 0)).to_string())
        print("\nip {} 总流量如下".format(sys.argv[2]))
        print(DataCore(aim_data).get_ip_traffic(limit=(0, 0)).to_string())
        print("\nip {} 各个状态码的访问次数如下".format(sys.argv[2]))
        print(DataCore(aim_data).get_ip_code_count(limit=(0, 0)).to_string())
    print("\n--数据分析耗时--")
    print(time.time()-b)
    print("--总耗时--")
    print(time.time()-a)





