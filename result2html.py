

import datetime
import sys
import os
import time
import json
import requests
from pandas import DataFrame
from urllib import quote



reload(sys)
sys.setdefaultencoding('utf8')

todaydate = datetime.datetime.now().strftime('%Y-%m-%d')

page_header = u'''
<html>
    <head>
        <title>
            Title-xxxxxxxx
        </title>
        <meta charset="utf-8">
    </head>
<body bgcolor="white">
    <hr>
    <pre>'''

page_content = '''<a href="%s">%s</a>
'''
page_content_result = []
currentIP = requests.get("http://ip.6655.com/ip.aspx").content
print currentIP
baseURI = "http://%s/deposit/%s_download/" % (currentIP, todaydate.replace("-",""))



# baseURL = "http://%s/deposit/%s_download/" % (currentIP, todaydate.replace("-",""))
page_footer = u'''        
    </pre>
    <hr>
</body>

</html>'''

for l in ["listed_code", "prepub_code"]:
    for i in os.listdir("/usr/pyoj/disclare/deposit/"
                                + todaydate.replace("-", "")
                                + "_download/"
                                + l):
        # print "/usr/pyoj/disclare/deposit/" + todaydate.replace("-", "") + "_download/" + l
        page_content_result.append(page_content % (baseURI + l + '/' + quote(i), i.replace(".pdf","")))

_page_sourcecode = page_header + "\n" \
                   + "".join(body_content for body_content in page_content_result) \
                   + "\n" + page_footer

with open("/usr/share/nginx/html/download_list.html", "w") as fp:
    fp.write(_page_sourcecode)
