#coding:utf-8

import scrapy
import datetime
import sys
sys.path.append('..\..')
from papers import settings
from papers.items import PaperItem,ArticleItem,PageItem,ImageItem
import re


class YNRBSpider(scrapy.Spider):
    name='YNRB'
    def start_requests(self):
        """取Setting文件设置生成start_requests"""
        date_format='%Y-%m-%d'
        now_date=datetime.datetime.now().strftime(date_format)
        try:
            ynrb_start_date_str=settings.ynrb_start_date
            ynrb_end_date_str=settings.ynrb_end_date
        except:
            ynrb_start_date_str=now_date
            ynrb_end_date_str=now_date
        ynrb_start_date=datetime.datetime.strptime(ynrb_start_date_str,date_format)
        ynrb_end_date=datetime.datetime.strptime(ynrb_end_date_str,date_format)
        days=(ynrb_end_date-ynrb_start_date).days+1
        i=0
        url_formt='http://yndaily.yunnan.cn/html/{0}/node_2.htm'
        requests=[]
        while i<days:
            d=ynrb_start_date+datetime.timedelta(i)
            url=url_formt.format(d.strftime('%Y-%m/%d'))
            requests.append(scrapy.Request(url,callback=self.paperParse,meta={'date':d}))
            i+=1
        return requests

    def paperParse(self,response):
        paper=PaperItem()
        paper['date']=response.meta['date']
        condition=response.xpath('//map[@name="PagePicMap"]')#新旧版判断条件
        if len(condition)>0:
            pages=[(page.xpath('text()').extract()[0],response.urljoin(page.xpath('@href').extract()[0])) for page in response.xpath('//div[@id="layer434"]//a[@id="pageLink"]')]
            #page_name,page_url
            paper['pages']=[]
            for page in pages:
                yield scrapy.Request(page[1],callback=pageParse1,meta={'paper':paper,'page_name':page[0]})
        else:
            pass
        return paper
    
    def pageParse(self,response):
        page_name=response.meta['page_name']
        paper=response.meta['paper']
        page=PageItem()
        page['title']=page_name
        
