#coding:utf-8
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
import scrapy

reUrl='./node_3.htm'
url='http://yndaily.yunnan.cn/html/2016-10/10/node_2.htm'
res=scrapy.http.Response(url=url)
print res.urljoin(reUrl)
#print dir(res)
#baseUrl=get_base_url(res)
#print urljoin_rfc(baseUrl,reUrl)