#!/usr/bin/python3
# -*- coding: utf-8 -*-
#导入SQLite驱动：
import sqlite3
class SqliteDB():
    def __init__(self):
        #连接数据库
        self.conn = sqlite3.connect('instance.db')
        #创建一个cursor：
        self.cursor = self.conn.cursor()
    def createTable(self,tabname,tabtype):
        if tabtype == 'ping':#创建ping测结果表
            sql = 'create table if not exists %s(ipaddress varchar(64),domain varchar(32),targethost varchar(32),mintime FLOAT,maxtime FLOAT,avgtime FLOAT,lossrate FLOAT,status varchar(32),timestamp varchar(32),nodename varchar(32))' %tabname
            print(sql)
        if tabtype == 'web':#创建web测试结果表
            sql = 'create table if not exists %s(url varchar(64),domain varchar(32),totaltime FLOAT,httptime FLOAT,nodename varchar(32),timestamp varchar(32))' %tabname
            print(sql)
        self.cursor.execute(sql)

    def insert(self,tabname):
        insert_data_sql = 'insert into %s(url,domain,totaltime,httptime,nodename,timestamp) values (:url,:domain,:totaltime,:httptime,:nodename,:timestamp)' %tabname
        l = "url,domain,totaltime,httptime,nodename,timestamp".split(',')
        tdata = 'http://www.u8e.com,www.u8e.com,8.86,0.098,zyx_lt,2020-07-07 16:49:08'.split(',')
        data = dict(zip(l,tdata))
        self.cursor.execute(insert_data_sql,data)
        self.conn.commit()
    def alter(self):
        update_sql = 'update happy set password = ? where username = ?'
        self.cursor.execute(update_sql,("4578623","ytouch"))
   
    def search(self,tabname):
        search_sql = "select * from %s" %tabname
        results = self.cursor.execute(search_sql)
        all_results  = results.fetchall()
        print(len(all_results))
        for happys in all_results:
            print(type(happys))  #type:tuple
            print(happys)

if __name__ == '__main__':
    db = SqliteDB()
    tabname = 'test'
    db.createTable(tabname = tabname,tabtype = 'web')

    #for i in range(0,10):
        #db.insert(tabname)

    db.search(tabname)