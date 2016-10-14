#coding:utf-8
#from scrapy.utils.project import get_project_settings#仅能导入默认KEY
import sys
sys.path.append('..')#更改当前工作目录
from papers.settings import *#载入settings.py文件

#setting=get_project_settings()
# start=setting.get('ynrb_start_date')
# bot=setting.get('BOT_NAME')
print ynrb_start_date