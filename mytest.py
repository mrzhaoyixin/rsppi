#!/usr/bin/python3
# -*- coding: utf-8 -*-
import runtest, mytrace,speedtest,time,os,sys,json,threading,requests,onenet,config

class pingThread (threading.Thread):
    def __init__(self, pinglist, indenttime = 10):
        threading.Thread.__init__(self)
        self.pinglist = pinglist
        self.indenttime = indenttime
    def ping(self,pinglist):
        with open("result/pingresult.txt","a") as pingres:
            onenetpr = []
            for i in pinglist:
                pingtimestamp = runtest.timestamp()
                pr = runtest.to_json(runtest.get_ping_result(i))
                pr["timestamp"] = pingtimestamp
                #目的域名 目标主机 目的IP 最小时延 平均时延 最大时延 收到包数量 丢包率 状态码(0正常，-1网络不可达，-2域名或地址错误) 时间戳 分类 终端编号 任务名
                pingres.write(str(pr)+"\n")
                onenetpr.append(pr)
            onenet.send_to_onenet(onenetpr,"pingresult")
            print(onenetpr)
    def run(self):
        while True:
            print("pingtest", threading.current_thread().name)
            self.ping(self.pinglist)
            time.sleep(self.indenttime)

class speedtestThread (threading.Thread):
    def __init__(self, nodeid = config.configure_speedtest.get("nodeID"), indenttime = 1800):
        threading.Thread.__init__(self)
        self.nodeid = nodeid
        self.indenttime = indenttime
    def myspdtest(self):
        if os.path.exists("result/speedtest.json"):
            f=open('result/speedtest.json', "a")
            t = runtest.timestamp()
            spdj = json.loads(runtest.get_speedtest_result(self.nodeid))
            onenet.send_to_onenet(spdj,"spdtestresult")
    def run(self):
        while True:
            
            self.myspdtest()
            time.sleep(self.indenttime)

class webtestThread(threading.Thread):
    def __init__(self, urllist,indenttime = 20):
        threading.Thread.__init__(self)
        self.indenttime = indenttime
        self.urllist = urllist
    def mywebtest(self):
        if os.path.exists("result/webtest.json"):
            f=open('result/webtest.json', "a")
            t = runtest.timestamp()
            webj = runtest.get_webtest_result(self.urllist)
            print(len(webj))
            web2onenetlist=[]
            for i in range(0,len(self.urllist)):
                calculate = {}
                web2onenet = {}
                calculate["redirecttime"] = (webj[i].get("redirectEnd")-webj[i].get("redirectStart"))/1000
				#TCP完成握手时间
                calculate["tcptime"] = (webj[i].get("connectEnd")-webj[i].get("connectStart"))/1000
				#DNS解析时间
                calculate["dnstime"] = (webj[i].get("domainLookupEnd")-webj[i].get("domainLookupStart"))/1000
				#HTTP请求响应完成时间
                calculate["httptime"] = (webj[i].get("responseEnd")-webj[i].get("requestStart"))/1000
				#DOM开始加载前所花费时间
                calculate["beforedomloadtime"] = (webj[i].get("responseEnd")-webj[i].get("navigationStart"))/1000
				#DOM加载完成时间
                calculate["domloadtime"] = (webj[i].get("domComplete")-webj[i].get("domLoading"))/1000
				#DOM结构解析完成时间
                calculate["domstructparsetime"] = (webj[i].get("domInteractive")-webj[i].get("domLoading"))/1000
				#脚本加载时间
                calculate["scriptloadtime"] = (webj[i].get("domContentLoadedEventEnd")-webj[i].get("domContentLoadedEventStart"))/1000
				#onload事件时间
                calculate["onloadeventtime"] = (webj[i].get("loadEventEnd")-webj[i].get("loadEventStart"))/1000
				#页面完全加载时间
                web2onenet["totaltime"] = calculate.get("redirecttime")+calculate.get("dnstime")+calculate.get("tcptime")+calculate.get("httptime")+calculate.get("domloadtime")+calculate.get("domstructparsetime")
                web2onenet["url"] = self.urllist[i]
                web2onenet["timestamp"] = t
                finaldict = {**calculate,**web2onenet}
                web2onenetlist.append(finaldict)
            onenet.send_to_onenet(web2onenetlist,"webtestresult")
    def run(self):
        while True:
            print("webtest", threading.current_thread().name)
            self.mywebtest()
            time.sleep(self.indenttime)

if __name__ == "__main__":
    #ping测试列表
    pinglist = ["www.baidu.com","www.taobao.com","www.jd.com"]
    #开启一个ping测线程 
    pingthread1 = pingThread( pinglist)
    pingthread1.start()
    #开启一个测速线程 
    #speedtestthread1 = speedtestThread()
    #speedtestthread1.start()
    #pingthread1.join()
    wtt = webtestThread(["http://www.taobao.com","http://github.com","http://www.hao123.com"])
    wtt.start()
    #res,unans = mytrace.get_trace_result("www.speedtest.net")
    #runtest.get_webtest_result("http://www.hebei.gov.cn")
