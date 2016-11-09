#coding:utf-8

import scrapy
import datetime
import sys
sys.path.append('..\..')
from papers import settings
from papers.items import PaperItem,ArticleItem,PageItem,ImageItem
import requests


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
                yield scrapy.Request(page[1],callback=self.pageParse1,meta={'paper':paper,'page_name':page[0]})
                print '---------------'
                print 'pages is %s' % len(paper['pages'])
        else:
            pass       
        yield paper
    
    def pageParse1(self,response):
        paper=response.meta['paper']
        page=PageItem()
        page['title']=response.meta['page_name']
        #padf版面url
        page_content_url=response.urljoin(response.xpath('//div[@class="fr mt3"]/a/@href')[0].extract())
        page_content=requests.get(page_content_url)
        #默认下载PDF版面,失败下载JPG版面,在失败返回空的jpg数据
        if not page_content.ok:
            #jpg版面url
            page_jpg_url=response.urljoin(response.xpath('//div[@id="picMap"]/img/@src')[0].extract())
            page_content=requests.get(page_jpg_url)
            if not page_content.ok:
                page['file_content']=''
                page['file_content']='jpg'
            else:
                page['file_type']='jpg'
        else:
            page['file_type']='pdf'
        page['file_content']=page_content.content
        page['articles']=[]
        #文章selectors
        articles_content=response.xpath('//div[@class="layer351"]//a')
        #文章(title,url)
        _articles=[(a.xpath('text()').extract()[0],response.urljoin(a.xpath('@href').extract()[0])) for a in articles_content]
        for art in _articles:
            yield scrapy.Request(art[1],callback=self.articleParse,meta={'abbrev_title':art[0],'page':page})
        paper['pages'].append(page)
        #yield page
        

    def articleParse(self,response):
        page=response.meta['page']
        article=ArticleItem()
        article['images']=[]
        article['content']=''.join(response.xpath('//div[@id="layer72"]/table/tr[last()]//*[name(.)!="script"]/text()').extract())
        article['title']='|'.join(response.xpath('//div[@id="layer72"]/table/tr[position()=1]//*/text()').extract())
        _imgs=response.xpath('//div[@id="layer72"]/table/tr[last()-1]/td/table/tr')
        #imgs(description,img/src,a/href) img/src像素低,a/href像素高
        imgs=[(''.join(img.xpath('.//*/text()').extract()),response.urljoin(img.xpath('.//img/@src').extract()[0]),response.urljoin(img.xpath('.//a/@href').extract()[0])) for img in _imgs]
        for img in imgs:
            yield scrapy.Request(img[2],callback=self.imageParse,meta={'article':article,'img_type':img[2][img[2].rfind('.')+1:],'img':img})
        page['articles'].append(article)
        #yield article

    def imageParse(self,response):
        article=response.meta['article']
        img=response.meta['img']
        img_type=response.meta['img_type']
        image=ImageItem()
        image['description']=img[0]
        if response.status==200:
            image['file_type']=img_type
            image['file_content']=response.body
        else:
            yield scrapy.Request(img[1],callback=self.imagePare,meta={'article':article,'img_type':img[1][img[1].rfind('.')+1:],'img':img})
        article['images'].append(image)        
        #yield image
        
   

        
