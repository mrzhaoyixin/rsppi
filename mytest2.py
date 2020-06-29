#!/usr/bin/python3
# -*- coding: utf-8 -*-
import runtest, mytrace,speedtest,time,os,sys,json,threading,requests,onenet,config,subprocess,re,multiprocessing
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from queue import Queue  
class pingClass():
    def __init__(self, pinglist, indenttime = 10):
        self.pinglist = pinglist
        self.indenttime = indenttime
        self.nodename = config.configure_ping.get('nodename')
    def get_ping_result(self, q, pcount="10", psize="32",timeout = "10"):
        try:
            ip_address=q
            timestamp = runtest.timestamp()
            p = subprocess.Popen(["ping", "-c", str(pcount), "-s", str(psize),"-W", str(timeout), ip_address], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
            out = p.stdout.read().decode('utf-8')
            reg_receive = '[0-9]* received'
            searchresult = re.search(reg_receive, out)
            if searchresult is not None:
                receivepkg = searchresult.group(0).split()[0]
                if int(receivepkg) > 0:
                    rtt = out.split("\n")[-2]
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
                        #目标主机 最小时延 平均时延 最大时延 收到包数量 丢包率 状态码 时间戳 终端号
                        #print([ip_address,domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate,'success'])
                        return [ip_address,domain, targethost, min_time, max_time, avg_time,  lossrate,'icmp_success', timestamp, self.nodename]
                    else:
                        targethost = out.split("\n")[0].split()[2][1:-1]
                        print("rttlist error:",rttlist)
                        return([ip_address, targethost, targethost, "-",  "-",  "-", "-", 'network_fail'])
                else:
                    #print('网络不通，目标服务器不可达！')
                    targethost = out.split("\n")[0].split()[2][1:-1]
                    tcplist = self.tcping(ip_address)
                    tcpreslist = [ip_address, targethost, targethost, timestamp, self.nodename]
                    tcpreslist[3:3] = tcplist
                    return tcpreslist
            else:
                #print("地址输入有错误",out)
                return [ip_address, ip_address, ip_address, "-",  "-",  "-",  "-", 'address_error', timestamp, self.nodename]
        except Exception as e:
            print(e)
    def write_file(self, result):
        resultlist = [str(x) for x in result]
        s = ','.join(resultlist)+'\n'
        #获取当前日期
        cudate = str(time.strftime("%Y-%m-%d", time.localtime()))
        with open('result/ping_'+cudate,'a') as f:
            f.write(s)
    def tcping(self,ipaddr):
        try:
            tcpp = subprocess.Popen(["tcping", "-c", '10', "-t", '10', ipaddr], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
            tcpout = tcpp.stdout.read().decode('utf-8')
            #print('tcpout',tcpout)
            outlist = tcpout.split("\n")
            #print('outlist-2',outlist[-2],'outelist-3',outlist[-3])
            min_time = outlist[-2].split(' = ')[1][0:4]
            max_time = outlist[-2].split(' = ')[2][0:4]
            avg_time = outlist[-2].split(' = ')[3][0:4]
            lossrate = 1-int(outlist[-3].split(' ')[2])/int(outlist[-3].split(' ')[0])
            if lossrate != 1:
                return [min_time,avg_time,max_time,lossrate,'tcping_success']
            return ['-','-','-','-','network_fail']
        except Exception as e:
            print('tcping error',e)
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
    def __init__(self, urllist,indenttime = 600):
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
            #chrome_options.add_argument('--disable-gpu')
            global driver
            driver = webdriver.Chrome(executable_path = '/usr/bin/chromedriver', chrome_options = chrome_options)
        except Exception as e:
            print("chrome_driver init error:",e)

    def mywebtest(self):
        #print('current Threading:',threading.current_thread().name)
        if os.path.exists("result/webtest.json"):
            f=open('result/webtest.json', "a") 
            for url in self.urllist:
                t = runtest.timestamp()
                try:
                    driver.get(url)
                    result = driver.execute_script("""
                           let mytiming = window.performance.timing;
                           return mytiming;
                           """)
                except Exception as e:
                    print('webtest error',e)
                    with open('result/webtest_'+cudate,'a') as webfile:
                        resultlist = [url,url[7:],'-','-',config.configure_speedtest.get('nodename'),t]
                        web_resultlist = [str(x) for x in resultlist]
                        s = ','.join(web_resultlist)+'\n'
                        print(s)
                        webfile.write(s)
                web2onenetlist=[]
                calculate = {}
                web2onenet = {}
                calculate["redirecttime"] = (result.get("redirectEnd")-result.get("redirectStart"))/1000
                #TCP完成握手时间
                calculate["tcptime"] = (result.get("connectEnd")-result.get("connectStart"))/1000
                #DNS解析时间
                calculate["dnstime"] = (result.get("domainLookupEnd")-result.get("domainLookupStart"))/1000
                #HTTP请求响应完成时间
                calculate["httptime"] = (result.get("responseEnd")-result.get("requestStart"))/1000
                #DOM开始加载前所花费时间
                calculate["beforedomloadtime"] = (result.get("responseEnd")-result.get("navigationStart"))/1000
                #DOM加载完成时间
                calculate["domloadtime"] = (result.get("domComplete")-result.get("domLoading"))/1000
                #DOM结构解析完成时间
                calculate["domstructparsetime"] = (result.get("domInteractive")-result.get("domLoading"))/1000
                #脚本加载时间
                calculate["scriptloadtime"] = (result.get("domContentLoadedEventEnd")-result.get("domContentLoadedEventStart"))/1000
                #onload事件时间
                calculate["onloadeventtime"] = (result.get("loadEventEnd")-result.get("loadEventStart"))/1000
                #页面完全加载时间
                web2onenet["totaltime"] = calculate.get("redirecttime")+calculate.get("dnstime")+calculate.get("tcptime")+calculate.get("httptime")+calculate.get("domloadtime")+calculate.get("domstructparsetime")
                web2onenet["url"] = url
                web2onenet["timestamp"] = t
                finaldict = {**calculate,**web2onenet}
                web2onenetlist.append(finaldict)
                cudate = str(time.strftime("%Y-%m-%d", time.localtime()))
                with open('result/webtest_'+cudate,'a') as webfile:
                    for i in web2onenetlist:
                        #url  域名 总时间 http响应时间 节点名称 
                        resultlist = [url,url[7:],i.get("totaltime"),i.get("httptime"),config.configure_speedtest.get('nodename'),i.get('timestamp')]
                        web_resultlist = [str(x) for x in resultlist]
                        s = ','.join(web_resultlist)+'\n'
                        print(s)
                        webfile.write(s)
            
            #onenet.send_to_onenet(web2onenetlist,"webtestresult")
    def run(self):
        #测试轮数
        count = 20
        while count>0:
            #print("webtest", threading.current_thread().name)
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
    #开启一轮多进程ping测
    #测试列表
    pinglist = []
    with open('pinglist.txt','r') as pingl:
        for i in pingl:
            pinglist.append(i[:-1])

    weblist = ['http://'+x for x in pinglist]
    wtt = webtestThread(weblist)
    wtt.start()

    pingcount = 50
    while pingcount>0:
        ping = pingClass(pinglist)
        pool = multiprocessing.Pool(processes = 100)
        for q in ping.pinglist:
            pool.apply_async(ping.get_ping_result, (q, ),callback=ping.write_file)
        pool.close()
        pool.join()
        time.sleep(300)
        pingcount = pingcount-1

    #开启一个测速线程 
    #speedtestthread1 = speedtestThread()
    #speedtestthread1.start()
    #pingthread1.join()
    #开启一轮web测试
    
    #res,unans = mytrace.get_trace_result("www.speedtest.net")
    #runtest.get_webtest_result("http://www.hebei.gov.cn")
