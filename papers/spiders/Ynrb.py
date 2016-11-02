#coding:utf-8

import scrapy
import datetime
import sys
sys.path.append('..\..')
from papers import settings
from papers.items import PaperItem,ArticleItem,PageItem,ImageItem,PageFileItem
from scrapy import log
import requests

class YNRBSpider(scrapy.Spider):
    name='ynrb'
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
                i=1
                for page in pages:
                    yield scrapy.Request(page[1],callback=self.pageParse1,meta={'paper':paper,'page_name':page[0],'serial_number':i})
                    i+=1                
            else:
                pass
    
    def pageParse1(self,response):#新版
        paper=response.meta['paper']
        serial_number=response.meta['serial_number']
        page=PageItem()
        page['paper']=paper
        page['title']=response.meta['page_name']
        page['serial_number']=serial_number
        #padf版面url
        page_file_url=response.urljoin(response.xpath('//div[@class="fr mt3"]/a/@href')[0].extract())
        #jpg版面url
        page_jpg_url=response.urljoin(response.xpath('//div[@id="picMap"]/img/@src')[0].extract())

        #默认下载PDF版面,失败下载JPG版面,在失败返回空的jpg数据
        yield scrapy.Request(page_file_url,callback=self.page_file_parse,meta={'page':page,'file_type':'pdf','page_jpg_url':page_jpg_url})
        #文章selectors
        articles_content=response.xpath('//div[@class="layer351"]//a')
        #文章(title,url)
        _articles=[(a.xpath('text()').extract()[0],response.urljoin(a.xpath('@href').extract()[0])) for a in articles_content]
        i=1
        for art in _articles:
            yield scrapy.Request(art[1],callback=self.articleParse,meta={'abbrev_title':art[0],'page':page,'serial_number':i})
            i+=1

    def page_file_parse(self,response):
        file_type=response.meta['file_type']
        page=response.meta['page']
        page_jpg_url=response.meta['page_jpg_url']
        serial_number=page['serial_number']
        pageFile=PageFileItem()
        pageFile['file_type']=file_type
        pageFile['serial_number']=serial_number

        if file_type=='pdf':
            if response.status!=200:
                yield scrapy.Request(page_jpg_url,callback=self.page_file_parse,meta={'page':page,'file_type':'jpg','page_jpg_url':page_jpg_url,'serial_number':serial_number})
            else:
                pageFile['content']=response.body
        else:
            if response.status!=200:
                pageFile['content']=''
            else:
                pageFile['content']=response.body
        yield pageFile
        
    def articleParse(self,response):
        page=response.meta['page']
        serial_number=response.meta['serial_number']
        article=ArticleItem()
        article['page']=page
        article['serial_number']=serial_number
        article['content']=''.join(response.xpath('//div[@id="layer72"]/table/tr[last()]//*[name(.)!="script"]/text()').extract())
        article['title']='|'.join(response.xpath('//div[@id="layer72"]/table/tr[position()=1]//*/text()').extract())
        #img selectors        
        _imgs=response.xpath('//div[@id="layer72"]/table/tr[last()-1]/td/table/tr')
        #imgs(description,img/src,a/href) img/src像素低,a/href像素高
        imgs=[(''.join(img.xpath('.//*/text()').extract()),response.urljoin(img.xpath('.//img/@src').extract()[0]).decode('gbk'),response.urljoin(img.xpath('.//a/@href').extract()[0])) for img in _imgs]
        i=1
        for img in imgs:
            yield scrapy.Request(img[2],callback=self.imageParse,meta={'article':article,'img_type':img[2][img[2].rfind('.')+1:],'img':img,'serial_number':i,'retry':False})
            i+=1
        yield article
    
    def imageParse(self,response):
        article=response.meta['article']
        img=response.meta['img']
        img_type=response.meta['img_type']
        serial_number=response.meta['serial_number']
        retry=response.meta['retry']
        image=ImageItem()
        image['description']=img[0]
        image['file_type']=img_type

        if response.status==200:
            image['file_content']=response.body
        else:
            if retry:
                image['file_content']=''
            else:
                yield scrapy.Request(img[1],callback=self.imagePare,meta={'article':article,'img_type':img[1][img[1].rfind('.')+1:],'img':img,'retry':True})
        yield image