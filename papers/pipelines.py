# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import items
import os
import codecs
import datetime


class PaperPipeline(object):

    def pjoin(self, path, *args):  # 文件\文件夹路径合并
        pa = os.path.join(path, *args)
        file = pa[pa.rfind('\\') + 1:]
        if not os.path.exists(pa):
            if file.find('.') > 0:
                p = pa[:pa.rfind('\\') + 1]
            else:
                p = pa
            if not os.path.isdir(p):
                try:
                    os.makedirs(p)
                except IOError, eMsg:
                    print eMsg
        return pa

    def saveFile(self, path, fileName, data, mode='txt'):  # 文件保存
        p = self.pjoin(path, fileName)
        if mode == 'txt':
            try:
                with codecs.open(p, 'w', 'utf-8') as f:
                    f.write(data)
            except BaseException, eMsg:
                print eMsg
        elif mode == 'bytes':
            try:
                with open(p, 'wb') as f:
                    f.write(data)
            except BaseException, eMsg:
                print eMsg
        else:
            print(u'%s文件写入失败,请指定正确文件类型' % p)

    def process_item(self, item, spider):
        if isinstance(item, items.ImageItem):
            description = item['description']
            file_type = item['file_type']
            file_content = item['file_content']
            art = item['art']
            art_no = art['serial_number']
            art_title = art['title']
            page = art['page']
            page_no = page['serial_number']
            date = page['date']
            sn = item['serial_number']
            path = self.pjoin('d:\\pap', '%s' % date.year, '%s-%02d' % (date.year, date.month),
                              '%s-%s-%02d' % (date.year, date.month, date.day), '%02d' % page_no, '%02d' % art_no)
            file_name = '%s%02d.%s' % (art_title, sn, file_type)
            self.saveFile(path, file_name, file_content, 'bytes')
        #return item
        if isinstance(item, items.PageFileItem):
            page = item['page']
            sn=page['serial_number']
            date=page['date']
            content = item['content']
            file_type = item['file_type']
            file_name='%s%-02d.%s' % (date.strftime('%Y%m%d'),sn,file_type)
            path = self.pjoin('d:\\pap\\rmrb', '%s' % date.year, '%s-%02d' % (date.year, date.month),
                              '%s-%s-%02d' % (date.year, date.month, date.day), 'pdf')
            self.saveFile(path, file_name, content, 'bytes')
            #print page['serial_number'], file_type, len(content)
