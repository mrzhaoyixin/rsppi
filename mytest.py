#!/usr/bin/python3
# -*- coding: utf-8 -*-
import runtest, mytrace,speedtest,time,os,sys,json,threading,requests,onenet,config,subprocess,re
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from queue import Queue  
class pingThread (threading.Thread):
    def __init__(self, pinglist, indenttime = 10):
        threading.Thread.__init__(self)
        self.pinglist = pinglist
        self.indenttime = indenttime
        global q
        q = Queue()
        for ip in self.pinglist:
            q.put(ip)
        self.q = q
    def get_ping_result(self, q, pcount="10", psize="32",timeout = "20"):
        print("pingtest", threading.current_thread().name)
        #print(self.q.qsize())
        ip_address=q.get()  
        print('get a addr ',ip_address,'remain ',self.q.qsize())
        p = subprocess.Popen(["ping", "-c", str(pcount), "-s", str(psize),"-W", str(timeout), ip_address], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        #p = subprocess.call('ping -c 1 -w 1 '+ip_address, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        out = p.stdout.read().decode('utf-8')
        #print(out)
        #with open("result/pingresulttemp","w+") as pingresult:
            #pingresult.write(out)
        reg_receive = '[0-9]* received'
        searchresult = re.search(reg_receive, out)
        
        if searchresult is not None:
            #print(searchresult)
            receivepkg = searchresult.group(0).split()[0]
            #print(receivepkg)
            if int(receivepkg) > 0:
                rtt = out.split("\n")[-2]
                #print("rtt:",rtt)
                r = rtt.split()
                if r[-2] is "pipe":
                    rttlist = r[-4].split("/")
                rttlist = r[-2].split("/")
                if len(rttlist)>2:
                    min_time = rttlist[0]
                    max_time = rttlist[1]
                    avg_time = rttlist[2]
                    lossrate = 1-int(receivepkg)/int(pcount)
                    domain = out.split("\n")[0].split()[1]
                    targethost = out.split("\n")[0].split()[2][1:-1]
                    #目标主机 最小时延 平均时延 最大时延 收到包数量 丢包率 状态码
                    print([ip_address,domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate, 0])
                    q.task_done()
                    return [ip_address,domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate, 0]
                else:
                    targethost = out.split("\n")[0].split()[2][1:-1]
                    print("rttlist error:",rttlist)
                    return([ip_address, targethost, targethost, "-",  "-",  "-",  "-",  "-", -1])
            else:
                print('网络不通，目标服务器不可达！')
                targethost = out.split("\n")[0].split()[2][1:-1]
                return [ip_address, targethost, targethost, "-",  "-",  "-",  "-",  "-", -1]
        else:
            print("地址输入有错误",out)
            return [ip_address, ip_address, ip_address, "-",  "-",  "-",  "-",  "-", -2]
    def ping(self,pinglist):
        with open("result/pingresult.txt","a") as pingres:
            onenetpr = []
            for i in range(4):
                pingtimestamp = runtest.timestamp()
                temp_t = threading.Thread(target=self.get_ping_result, args=(self.q,))
                temp_t.start()
                '''
                ping_res = self.get_ping_result(i)
                print(ping_res)
                pr = runtest.to_json(ping_res)
                pr["timestamp"] = pingtimestamp
                #目的域名 目标主机 目的IP 最小时延 平均时延 最大时延 收到包数量 丢包率 状态码(0正常，-1网络不可达，-2域名或地址错误) 时间戳 分类 终端编号 任务名
                pingres.write(str(pr)+"\n")
                onenetpr.append(pr)
            onenet.send_to_onenet(onenetpr,"pingresult")
            print(onenetpr)
            '''
    def run(self):
        while True:
            print("pingtest", threading.current_thread().name)
            if self.q.qsize() == 0:
                print('reputting ip')
                for ip in self.pinglist:
                    self.q.put(ip)
            self.ping(self.q)
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
#网页测试线程
class webtestThread(threading.Thread):
    def __init__(self, urllist,indenttime = 0):
        threading.Thread.__init__(self)
        self.indenttime = indenttime
        self.urllist = urllist
        #初始化chromedirver
        try:
            global chrome_options
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            #chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("–incognito")
            #chrome_options.add_argument('blink-settings=imagesEnabled=false')
            chrome_options.add_argument('--disable-gpu')
            global driver
            driver = webdriver.Chrome(executable_path = '/usr/bin/chromedriver', chrome_options = chrome_options)
        except Exception as e:
            print("chrome_driver init error:",e)

    def mywebtest(self):
        print('current Threading:',threading.current_thread().name)
        if os.path.exists("result/webtest.json"):
            f=open('result/webtest.json', "a")
            t = runtest.timestamp()
            print(t)
            testresult=[]
            try:    
                for url in self.urllist:
                    print('begin test',runtest.timestamp())
                    print('geturl :',url)
                    driver.get(url)
                    print('exec script')
                    result = driver.execute_script("""
                           let mytiming = window.performance.timing;
                           return mytiming;
                           """)
                    print('end test',runtest.timestamp())
                    testresult.append(result)
            except Exception as e:
                print("web test error:",e)
            #print(testresult)
            
            #webj = runtest.get_webtest_result(self.urllist)
            webj = testresult
            print(len(webj))
            web2onenetlist=[]
            for i in range(0,len(webj)):
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
            print(web2onenetlist)
            onenet.send_to_onenet(web2onenetlist,"webtestresult")
    def run(self):
        count = 2000
        while count>0:
            print("webtest", threading.current_thread().name)
            self.mywebtest()
            #t1 = threading.Thread(target=self.mywebtest())
            #t1.start()
            time.sleep(self.indenttime)
            count = count-1
            print(count,'times left')
        driver.quit()
if __name__ == "__main__":
    #ping测试列表
    #pinglist = ["www.baidu.com","www.taobao.com","www.jd.com","www.baidu.com","www.taobao.com","www.jd.com","www.baidu.com","www.taobao.com","www.jd.com","www.baidu.com","www.taobao.com","www.jd.com"]
    #开启一个ping测线程 
    pinglist = []
    with open('pinglist.txt','r') as pingl:
        for i in pingl:
            pinglist.append(i[:-1])
    pingthread1 = pingThread(pinglist)
    pingthread1.start()
    #开启一个测速线程 
    #speedtestthread1 = speedtestThread()
    #speedtestthread1.start()
    #pingthread1.join()
    #wtt = webtestThread(["http://www.taobao.com","http://github.com","http://www.hao123.com"])
    #wtt.start()
    #res,unans = mytrace.get_trace_result("www.speedtest.net")
    #runtest.get_webtest_result("http://www.hebei.gov.cn")
