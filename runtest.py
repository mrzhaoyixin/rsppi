#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys,subprocess,re,config,time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def get_speedtest_result(nodeid):
    if nodeid is None:
        p = subprocess.Popen(["speedtest",  "--format=json"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        out = p.stdout.read().decode('utf-8')
        return out
    else:
        p = subprocess.Popen(["speedtest", "--server-id", str(nodeid), "--format=json"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
        out = p.stdout.read().decode('utf-8')
        return out

def get_ping_result(ip_address, pcount="8", psize="32",timeout = "20"):
    p = subprocess.Popen(["ping", "-c", str(pcount), "-s", str(psize),"-W", str(timeout), ip_address], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
    out = p.stdout.read().decode('utf-8')
    #with open("result/pingresulttemp","w+") as pingresult:
        #pingresult.write(out)
    reg_receive = '\d received'
    searchresult = re.search(reg_receive, out)
    
    if searchresult is not None:
        receivepkg = searchresult.group(0).split()[0]
        if int(receivepkg) > 0:
            rtt = out.split("\n")[-2]
            print("rtt:",rtt)
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
                #目标主机 最小时延 最大时延 平均时延 收到包数量 丢包率 状态码
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
        print("地址输入有错误")
        return [ip_address, ip_address, ip_address, "-",  "-",  "-",  "-",  "-", -2]
def get_webtest_result(weburl):
    testresult=[]
    for url in weburl:
        try:
            
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--headless')
            #chrome_options.add_argument('blink-settings=imagesEnabled=false')
            #chrome_options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(chrome_options = chrome_options)
            start = time.time()
            driver.get(url)
            elapse = time.time()-start
            result = driver.execute_script("""
                   let mytiming = window.performance.timing;
                   return mytiming;
                   """)
            testresult.append(result)
            driver.quit()
        except Exception as e:
            print("web test error:",e)
    print(testresult)
    return testresult
        

def to_json(ping_result = []):
    ping_dict_key = ["domain","cnamedomain", "targethost", "min_time", "max_time", "avg_time", "receivepkg", "lossrate", "statuscode"]
    dict_result = dict(zip(ping_dict_key,ping_result))
    dict_result_merged_config = dict( dict_result, **config.configure_ping )
    return(dict_result_merged_config)
if __name__ == '__main__':
    '''
    print("ping start")
    arglist = sys.argv[1:]
    print("args:",arglist)
    for ip in arglist:
        print(to_json(get_ping_result(ip)))
    '''
