# -*- coding: utf-8 -*-
# Author pipixia


import datetime
import json
import sys
import re
import threading
import time
import os
import requests
from lxml import etree
from get_reports_server import getReports

'''
阿里云用 取消去重部分代码
输出发行基本信息至网页
'''

reload(sys)
sys.setdefaultencoding('utf8')

startdate = datetime.datetime.now().strftime('%Y-%m-%d')
modifydays = datetime.timedelta(days=+30)
enddate = (datetime.datetime.now()+modifydays).strftime('%Y-%m-%d')
session = requests.Session()
header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2453.0 Safari/537.36",
          "Host": "www.chinamoney.com.cn"}

dirs_name_list = ["prepub_code", "listed_code"]


for i in dirs_name_list:
    try:
        os.makedirs("/usr/pyoj/disclare/deposit/" + startdate.replace("-","") + "_download/" + i)
    except Exception:
        pass


class Get_Prepub_Code(object):

    def __init__(self):
        self._result = None
        self.result = None

    def run(self):

        print "Pre-pub Start at " + str(time.ctime())
        _modifydays = datetime.timedelta(days=+1)
        _startdate = (datetime.datetime.now()+_modifydays).strftime('%Y-%m-%d')

        prepub_url = "http://www.chinamoney.com.cn/ags/ms/cm-u-member-an/MarketSelfDisciplineDepositToIssue"

        pst_Data = {"beginDate": _startdate,
                    "endDate": enddate,
                    "pageSize": 30,
                    "pageNo": 1}

        session.headers.update(header)
        res = session.post(prepub_url, data=pst_Data).content
        pageno = json.loads(res).get("data").get("pageTotalSize")

        prepub_codelist = []
        for i in range(1, pageno + 1):
            pst_Data["pageNo"] = i
            _content = session.post(prepub_url, data=pst_Data).content
            prepub_codelist.extend([(j.get("bondDfndcd"), j.get("bondCode"))
                                    for j in json.loads(_content).get("records")])

        self.result = prepub_codelist

    def get_return(self):
        '''
        try:
            fp = open("prepub_outputlist" + startdate + ".txt", "r")
            _compare = [unicode(p.strip()) for p in fp.readlines()]
            _result = []
            for r in self.result:
                if r[0] not in _compare:
                    _result.append(r)
                else:
                    continue
            self._result = _result

            fp = open("prepub_outputlist" + startdate + ".txt", "w+")
            fp.write("\n".join(ii[0] for ii in self.result))
            fp.close()

            return self._result
        except Exception:
            fp = open("prepub_outputlist" + startdate + ".txt", "w+")
            fp.write("\n".join(ii[0] for ii in self.result))
            fp.close()
            return self.result
        '''
        with open("/usr/pyoj/disclare/deposit/prepub_outputlist" + startdate + ".txt", "w") as fp:
            fp.write("\n".join(ii[0] for ii in self.result))

        return self.result

class Get_Listed_Code(object):

    def __init__(self):
        self._result = None
        self.result = None

    def run(self):

        print "Listed Start at " + str(time.ctime())
        listed_url = "http://www.chinamoney.com.cn/ags/ms/cm-u-member-an/MarketSelfDisciplineDepositIsIssued"

        pst_Data = {"beginDate": startdate,
                    "endDate": enddate,
                    "pageSize": 30,
                    "pageNo": 1}

        session.headers.update(header)
        # aaaa = session.post(listed_url, data=data).content

        res = session.post(listed_url, data=pst_Data).content
        pageno = json.loads(res).get("data").get("pageTotalSize")

        listed_codelist = []
        for i in range(1, pageno + 1):
            pst_Data["pageNo"] = i
            _content = session.post(listed_url, data=pst_Data).content
            listed_codelist.extend([(j.get("bondDfndcd"), j.get("bondCode"))
                                    for j in json.loads(_content).get("records")])

        self.result = listed_codelist

    def get_return(self):
        '''
        try:
            fp = open("listed_outputlist" + startdate + ".txt", "r")
            _compare = [unicode(p.strip()) for p in fp.readlines()]
            _result = []
            for r in self.result:
                if r[0] not in _compare:
                    _result.append(r)
                else:
                    continue
            self._result = _result

            fp = open("listed_outputlist" + startdate + ".txt", "w+")
            fp.write("\n".join(ii[0] for ii in self.result))
            fp.close()

            return self._result
        except Exception:
            fp = open("listed_outputlist" + startdate + ".txt", "w+")
            fp.write("\n".join(ii[0] for ii in self.result))
            fp.close()
            return self.result
        '''
        with open("/usr/pyoj/disclare/deposit/listed_outputlist" + startdate + ".txt", "w") as fp:
            fp.write("\n".join(ii[0] for ii in self.result))

        return self.result


if __name__ == "__main__":
    # 获取报告列表
    Prepub_Proc = Get_Prepub_Code()
    Listed_Proc = Get_Listed_Code()

    # 处理预发行 已发行报告列表
    thd = []
    thd.append(threading.Thread(target=Prepub_Proc.run()))
    thd.append(threading.Thread(target=Listed_Proc.run()))

    for t in thd:
        t.setDaemon(True)
        t.start()

    # 报告列表处理完成
    PrepubReturn = Prepub_Proc.get_return()
    ListedReturn = Listed_Proc.get_return()
    print "Phrase1 Finished! at " + str(time.ctime())

    # 获取报告链接 提取预发行债券基本信息
    thd = []
    Prepub_Proc_Report = getReports(PrepubReturn)
    Listed_Proc_Report = getReports(ListedReturn)
    thd.append(threading.Thread(target=Prepub_Proc_Report.getReportList()))
    thd.append(threading.Thread(target=Listed_Proc_Report.getReportList()))
    thd.append(threading.Thread(target=Prepub_Proc_Report.getBaseInfo()))

    for t in thd:
        t.setDaemon(True)
        t.start()

    print "Phrase2 Finished! at " + str(time.ctime())


    prepub_codes = Prepub_Proc_Report.get_result()
    list_codes = Listed_Proc_Report.get_result()

    thd = []
    thd.append(threading.Thread(target=Prepub_Proc_Report.prepub_download_process, args=(prepub_codes,)))
    thd.append(threading.Thread(target=Listed_Proc_Report.listed_download_process, args=(list_codes,)))

    
    for t in thd:
        t.setDaemon(True)
        t.start()

    for _t in thd:
        _t.join()
    
    # Prepub_Proc_Report.result_to_html()
    os.system("python /usr/pyoj/chinamoneydeposit/result2html.py")
    print "Finished at " + str(time.ctime())
    
    # raw_input()
