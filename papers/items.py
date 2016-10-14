# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ImageItem(scrapy.Item):
    name=scrapy.Field()
    file_content=scrapy.Field()
    file_type=scrapy.Field()
    description=scrapy.Field()

class ArticleItem(scrapy.Item):
    title=scrapy.Field()
    author=scrapy.Field()
    copyright=scrapy.Field()
    images=scrapy.Field()
    content=scrapy.Field()

class PageItem(scrapy.Item):
    title=scrapy.Field()
    file_content=scrapy.Field()
    file_type=scrapy.Field()
    articles=scrapy.Field()

class PaperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date=scrapy.Field()
    pages=scrapy.Field()