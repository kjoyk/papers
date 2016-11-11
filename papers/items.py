# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImageItem(scrapy.Item):
    file_content = scrapy.Field()
    file_type = scrapy.Field()
    description = scrapy.Field()
    art = scrapy.Field()
    serial_number = scrapy.Field()


class ArticleItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    page = scrapy.Field()
    serial_number = scrapy.Field()


class PageItem(scrapy.Item):
    title = scrapy.Field()
    serial_number = scrapy.Field()
    date=scrapy.Field()


# class PaperItem(scrapy.Item):
#     # define the fields for your item here like:
#     date = scrapy.Field()


class PageFileItem(scrapy.Item):
    content = scrapy.Field()
    file_type = scrapy.Field()
    page=scrapy.Field()