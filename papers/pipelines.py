# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import items

class PaperPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item,items.PaperItem):
            for p in item['pages']:
                print '----------------'
                print p['title'],len(p['articles'])
                print '---------------------------'
        return item