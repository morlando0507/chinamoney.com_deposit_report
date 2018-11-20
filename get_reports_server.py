# -*- coding: utf-8 -*-
# Author pipixia

import datetime
import sys
import grequests
import os
import time
import json
import requests
from pandas import DataFrame
from lxml import etree
from urllib import quote


reload(sys)
sys.setdefaultencoding('utf8')


class getReports(object):

    def __init__(self, codelist_box):
        self.todaydate = datetime.datetime.now().strftime('%Y-%m-%d')
        self.details_url = "http://www.chinamoney.com.cn/fe/jsp/CN/chinamoney/market/searchBondDetailInfo.jsp?bondDefinedCode="
        self.baseurl = "http://www.chinamoney.com.cn"
        self.session = requests.Session()
        self.codelist_box = codelist_box
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2453.0 Safari/537.36",
            "Host": "www.chinamoney.com.cn"}
        self.result = None

    def list_filter(self, c):
        if c[1].find("download=") > -1:
            return c

    def getReportList(self):

        self.session.headers.update(self.header)
        download_list = []

        relatedURL= "http://www.chinamoney.com.cn/dqs/rest/cm-u-notice-md/BondRelatedContent"
        pst_data = {"bondDefinedCode": "",
                    "secondType": "0601,0602,0701,1001,1103,1104,1301,1302,1303,1304,2001,2002"}

        print "get_reports_list start at " + time.ctime()

        download_URL = "http://www.chinamoney.com.cn/dqs/cm-s-notice-query/fileDownLoad.do?contentId=%s&priority=0&mode=open"

        for cl in self.codelist_box:
            pst_data["bondDefinedCode"] = cl[0]
            # print cl[0]
            temp_res = json.loads(self.session.post(relatedURL, data=pst_data).content).get("data").get("resultList")

            if len(temp_res) >= 1:
                for j in temp_res:
                    download_list.append((j["title"], j["contentId"], download_URL % j["contentId"]))
            else:
                print "%s No report." % str(cl[0])

        print "get_reports_list end at " + time.ctime()
        self.result = download_list
        print len(download_list)

    def get_result(self):
        return self.result

    def prepub_download_process(self, download_box):
        print self.todaydate.replace("-", "")

        for dp in download_box:
            try:
                fp = open("/usr/pyoj/disclare/deposit/"
                          + self.todaydate.replace("-","") + "_download/prepub_code/"
                          + dp[0] + ".pdf", "wb")
                _ct = self.session.get(dp[2]).content
                time.sleep(2)
                fp.write(_ct)
                fp.close()
            except IOError:
                continue

    def listed_download_process(self, download_box):
        print self.todaydate.replace("-","")

        for dp in download_box:
            if dp[0].find(u'发行情况公告') > -1:
                try:
                    fp = open("/usr/pyoj/disclare/deposit/"
                              + self.todaydate.replace("-","") + "_download/listed_code/"
                              + dp[0] + ".pdf", "wb")
                    _ct = self.session.get(dp[2]).content
                    time.sleep(2)
                    fp.write(_ct)
                    fp.close()
                except IOError:
                    continue
            else:
                continue

    def getBaseInfo(self):

        # 网页内容变更,以下为陈旧代码
        ''' 
        wb = Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sheet1', cell_overwrite_ok=True)

        self.session.headers.update(self.header)
        urllist_box = [self.details_url + cl[0] for cl in self.codelist_box]

        rs = [grequests.get(cl, session = self.session) for cl in urllist_box]
        grequests.map(rs, size = 10)
        content_result = [cr.response.content for cr in rs]

        base_info_elements = {0: u"债券全称",
                              1: u"债券简称",
                              2: u"债券代码",
                              3: u"发行人",
                              4: u"债券类型",
                              5: u"债券发行日",
                              6: u"到期兑付日",
                              7: u"上市交易日",
                              8: u"债券摘牌日",
                              9: u"债券期限",
                              10: u"流通范围",
                              11: u"面值(元)",
                              12: u"发行价格(元)",
                              13: u"计划发行量(亿)",
                              14: u"实际发行量(亿)",
                              15: u"币种",
                              16: u"计息基础",
                              17: u"息票类型",
                              18: u"债券起息日",
                              19: u"付息频率",
                              20: u"票面利率(%)",
                              21: u"发行收益率(%)",
                              22: u"参考收益率(%)",
                              23: u"基准利率",
                              24: u"基准利差(BP)",
                              25: u"信用评级机构一",
                              26: u"债项/主体评级一",
                              27: u"信用评级机构二",
                              28: u"债项/主体评级二",
                              29: u"行权类型",
                              30: u"行权日期",
                              31: u"托管机构",
                              32: u"备注"}
        result_box = []
        print "get_base_info start at " + time.ctime()

        for cl in content_result:
            result_dict = {}
            p = re.compile(r"<[/]?a.*?>")
            source_code = p.sub("", cl)
            req = etree.HTML(source_code)
            fullname = req.xpath("//td[@class='mbr-title center']/text()")
            content_box = [pp.strip()
                           for pp in req.xpath("//td[@class='bdr-dtail' and @align='center']//td/text()")]
            # print content_result.index(cl)
            for i in range(len(content_box)):
                if content_box[i] in base_info_elements.values():
                    result_dict[content_box[i]] = content_box[i + 1]
            result_dict[u"债券全称"] = fullname[0]

            result_box.append(result_dict)

        for title in base_info_elements.values():
            ws.write(0, base_info_elements.values().index(title), title.strip())

        for r in result_box:
            for ee in base_info_elements.values():
                try:
                    ws.write(result_box.index(r) + 1, base_info_elements.values().index(ee), r[ee].strip())
                except KeyError:
                    ws.write(result_box.index(r) + 1, base_info_elements.values().index(ee), "N/A")
                    
        '''

        # 空列表存放baseinfo
        bondbaseinfo_list = []

        for bond_defcode in self.codelist_box:
            bondinfo_URL = "http://www.chinamoney.com.cn/dqs/rest/cm-u-bond-md/BondDetailInfo"
            pst_InfoData = {"bondDefinedCode": bond_defcode}

            bondbaseinfo = json.loads(self.session.post(bondinfo_URL, data=pst_InfoData).content).get("data").get("bondBaseInfo")

            try:
                for i, j in enumerate(bondbaseinfo.get("creditRateEntyList")):
                    bondbaseinfo["creditEntyFullName" + str(i)] = j.get("entyFullName")
                    bondbaseinfo["creditEntyDefinedCode" + str(i)] = j.get("entyDefinedCode")
                    bondbaseinfo["creditEntySubRating" + str(i)] = j.get("creditSubjectRating")
            except KeyError:
                bondbaseinfo["creditEntyFullName0"] = "N/A"
                bondbaseinfo["creditEntyDefinedCode0"] = "N/A"
                bondbaseinfo["creditEntySubRating0"] = "N/A"

            try:
                for m, n in enumerate(bondbaseinfo.get("exerciseInfoList")):
                    bondbaseinfo["exerciseDate" + str(m)] = n.get("exerciseDate")
                    bondbaseinfo["exerciseType" + str(m)] = n.get("exerciseType")
            except KeyError:
                bondbaseinfo["exerciseDate0"] = "N/A"
                bondbaseinfo["exerciseType0"] = "N/A"

            bondbaseinfo.pop("creditRateEntyList")
            bondbaseinfo.pop("exerciseInfoList")

            bondbaseinfo_list.append(bondbaseinfo)
        df = DataFrame(bondbaseinfo_list)
        df.to_html("/usr/share/nginx/html/index.html")
        print "get_base_info end at " + time.ctime()

    def result_to_html(self):
        page_header = u'''
        <html>
            <head>
                <title>
                    货币网-同业存单
                </title>
                <meta charset="utf-8">
            </head>
        <body bgcolor="white">
            <hr>
            <pre>'''

        page_content = '''<a href="%s">%s</a>
'''
        page_content_result = []
        currentIP = self.session.get("http://ip.6655.com/ip.aspx").content
        print currentIP
        baseURI = "http://%s/deposit/%s_download/" % (currentIP, self.todaydate.replace("-",""))

        page_footer = u'''        
            </pre>
            <hr>
        </body>

        </html>'''

        for l in ["listed_code", "prepub_code"]:
            for i in os.listdir("/usr/pyoj/disclare/deposit/"
                                        + self.todaydate.replace("-","")
                                        + "_download/"
                                        + l):
                page_content_result.append(page_content % (baseURI + l + '/' + quote(i), i))

        _page_sourcecode = page_header + "\n" \
                           + "".join(body_content for body_content in page_content_result) \
                           + "\n" + page_footer

        with open("/usr/share/nginx/html/download_list.html", "w") as fp:
            fp.write(_page_sourcecode)

