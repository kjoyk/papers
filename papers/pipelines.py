# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import items
import os
import codecs

class PaperPipeline(object):
    def saveFile(self,path,fileName,data,mode='txt'):#文件保存
        p=self.pjoin(path,fileName)
        if mode=='txt':
            try:
                with codecs.open(p,'w','utf-8') as f:
                    f.write(data)
            except BaseException,eMsg:
                print eMsg
        elif mode=='bytes':
            try:
                with open(p,'wb') as f:
                    f.write(data)
            except BaseException,eMsg:
                print eMsg
        else:
            pirnt u'%s文件写入失败,请指定正确文件类型' % p

    def pjoin(self,path,*args):#文件\文件夹路径合并
        pa=os.path.join(path,*args)
        file=pa[pa.rfind('\\')+1:]
        if not os.path.exists(pa):
            if file.find('.')>0:
                p=pa[:pa.rfind('\\')+1]
            else:
                p=pa
            if not os.path.isdir(p):
                try:
                    os.makedirs(p)
                except IOError,eMsg:
                    print eMsg
        return pa

    def process_item(self, item, spider):        
        if isinstance(item,items.ImageItem):
            print '------------'
            print item['description']
            print '--------------'
        #return item