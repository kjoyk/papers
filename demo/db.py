#coding:utf-8
import pymssql

class MSSQL:
    def __init__(self,host,user,pwd,db):
        self.host=host
        self.user=user
        self.pwd=pwd
        self.db=db
    def __GetConnect():
        if
    

cnn=pymssql.connect(host='127.0.0.1\\yxda',user='sa',password='111111')
sql="""if not exists(select * from sys.databases where name='Papers')
begin
	create database Papers
	on
	primary
	(
		name='Papers',
		filename='d:\\data\\Papers_data.mdf'
	)
	log	on
	(
		name='Papers_log',
		filename='d:\\data\\Papers_log.ldf'
	)
end"""
