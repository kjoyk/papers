# coding:utf-8

import scrapy
import datetime
import sys
sys.path.append('..\\..')
from papers import settings
from papers.items import ArticleItem, PageItem, ImageItem, PageFileItem
from PIL import Image
import StringIO
import pytesseract


class RMRBSpider(scrapy.Spider):
    '''人民日报'''
    name = 'rmrb'

    def start_requests(self):
        """取Setting文件设置生成start_requests"""
        date_format = '%Y-%m-%d'
        date_now = datetime.datetime.now().strftime(date_format)
        try:
            start_date_str = settings.rmrb_start_date
            end_date_str = settings.rmrb_end_date
        except:
            start_date_str = date_now
            end_date_str = date_now
        start_date = datetime.datetime.strptime(start_date_str, date_format)
        end_date = datetime.datetime.strptime(end_date_str, date_format)
        days = (end_date - start_date).days + 1
        url_format = 'http://paper.people.com.cn/rmrb/html/%s/nbs.D110000renmrb_01.htm'
        i = 0
        requests = []
        while i < days:
            day = start_date + datetime.timedelta(i)
            url = url_format % day.strftime('%Y-%m/%d')
            requests.append(scrapy.Request(
                url=url, callback=self.Parse, meta={'date': day}))
            i += 1
        return requests

    def Parse(self, response):
        '''初始页面解析'''
        date = response.meta['date']
        pageItem = PageItem()
        pageItem['date'] = date
        _pages = response.xpath('//div[@id="pageList"]/ul/div/div[1]/a')
        pages = [(page.xpath('text()').extract()[0], response.urljoin(page.xpath('@href').extract()[
                  0]), page.xpath('../../div[2]/a/@href').extract()[0][9:]) for page in _pages]
        # page_name,page_url,page_file
        for i, page in enumerate(pages, 1):
            pageItem['serial_number'] = i
            pageItem['title'] = page[0]
            if i == 1:
                response.meta['page'] = pageItem
                response.meta['page_file']=page[2]
                for p in self.pageParse(response):
                    yield p
            else:
                yield scrapy.Request(page[1], callback=self.pageParse, meta={'page': pageItem, 'page_file': page[2]})

    def pageParse(self, response):
        """版面解析"""
        codeUrl = r'http://paper.people.com.cn/pdfcheck/validatecodegen'
        page = response.meta['page']
        page_file = response.meta['page_file']
        page_jpg_url = response.urljoin(response.xpath(
            '//div[@class="ban"]//img/@src').extract()[0])
        yield scrapy.Request(codeUrl, callback=self.pageFileParse, meta={'page': page, 'file_type': 'pdf', 'code': '', 'page_file': page_file, 'page_jpg_url': page_jpg_url})

    def pageFileParse(self, response):
        """版面文件下载"""        
        #定义常量
        codeUrl = r'http://paper.people.com.cn/pdfcheck/validatecodegen'
        fnUrl = r'http://paper.people.com.cn/pdfcheck/check/checkCode.jsp'
        
        #meta取值
        file_type = response.meta['file_type']
        code = response.meta['code']
        page=response.meta['page']
        page_file = response.meta['page_file']
        page_jpg_url = response.meta['page_jpg_url']

        #PageFileItem赋值
        pageFile = PageFileItem()
        pageFile['file_type'] = file_type
        pageFile['page'] = page
        if code == '':
            image = Image.open(StringIO.StringIO(response.body))
            code = pytesseract.image_to_string(image)
            if len(code) != 4:
                yield scrapy.Request(codeUrl, callback=self.pageFileParse, meta={'page': page, 'file_type': 'pdf', 'code': '', 'page_file': page_file, 'page_jpg_url': page_jpg_url})
            else:
                bod='filename=%s&checkCode=%s' % (page_file,code)
                yield scrapy.Request(fnUrl, method='POST',body=bod,callback=self.pageFileParse, meta={'page': page, 'file_type': 'pdf', 'code': code, 'page_file': page_file, 'page_jpg_url': page_jpg_url})
        else:
            if file_type == 'pdf':
                if response.status != 200:
                    yield scrapy.Request(page_jpg_url, callback=self.pageFileParse, meta={'page': page, 'file_type': 'jpg', 'code': code, 'page_file': '', 'page_jpg_url': ''})
                    # pdf版面获取失败,则获取JPG版面
                else:
                    pageFile['content'] = response.body
            else:
                if response.status != 200:
                    # JPG版面获取失败,则返回空值
                    pageFile['content'] = ''
                else:
                    pageFile['content'] = response.body
            yield pageFile
