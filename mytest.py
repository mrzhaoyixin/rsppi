import myping, mytrace,speedtest,time,os,sys,json,myspeedtest,threading
def timestamp():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
class pingThread (threading.Thread):
    def __init__(self, pinglist,  name = "ping测试任务", indenttime = 60):
        threading.Thread.__init__(self)
        self.name = name
        self.pinglist = pinglist
        self.indenttime = indenttime
    def ping(self,pinglist):
        with open("result/pingresult.txt","a") as pingres:
            for i in pinglist:
                pr = myping.get_ping_result(i)
                '''
                if pr is None:
                    pr = [i,i,i,"-","-","-","-","-"]
                    pr.append(timestamp())
                    pr.append("PingTest")
                    pr.append("zyx_lt")
                    pr.append(self.name)
                    print(pr)
                    pr = map(lambda x:str(x),pr)
                    pingres.write("|".join(pr)+"\n")
                    continue
                '''
                if len(pr):
                    pr.insert(0,i)
                    pr.append(timestamp())
                    pr.append("PingTest")
                    pr.append("zyx_lt")
                    pr.append(self.name)
                    print(pr)
                    pr = map(lambda x:str(x),pr)
                    #目的域名 目标主机 目的IP 最小时延 平均时延 最大时延 收到包数量 丢包率 状态码(0正常，-1网络不可达，-2域名或地址错误) 时间戳 分类 终端编号 任务名
                    pingres.write("|".join(pr)+"\n")
    def run(self):
        while True:
            self.ping(self.pinglist)
            time.sleep(self.indenttime)



class speedtestThread (threading.Thread):
    def __init__(self, nodeid = 17223,  name = "speedtest测试任务", indenttime = 900):
        threading.Thread.__init__(self)
        self.name = name
        self.nodeid = nodeid
        self.indenttime = indenttime
    def myspdtest(self, nodeid = 17223):
        if os.path.exists("result/speedtest.json"):
            f=open('result/speedtest.json', "r+")
            f.truncate()
            t = timestamp()
            spdj = json.loads(myspeedtest.get_speedtest_result(nodeid))
            with open("result/speedtest.txt","a") as spdres:
                spdl = []
                spdl.append(spdj.get("server").get("id"))
                spdl.append(spdj.get("server").get("host"))
                spdl.append(spdj.get("server").get("ip"))
                spdl.append(spdj.get("interface").get("externalIp"))
                spdl.append(spdj.get("ping").get("latency"))
                spdl.append(spdj.get("ping").get("jitter"))
                spdl.append(spdj.get("download").get("bandwidth")*8/1024/1024)
                spdl.append(spdj.get("upload").get("bandwidth")*8/1024/1024)
                spdl.append(spdj.get("result").get("url"))
                spdl.append(t)
                spdl.append("SpeedTest")
                spdl.append("zyx_lt")
                spdl.append(self.name)
                print(spdl)
                spdl = map(lambda x:str(x),spdl)
                #服务器ID 主机名 服务器IP 本机公网IP ping时延 抖动 下载带宽 上传带宽 测试结果URL 时间戳 分类 终端编号 任务名
                spdres.write("|".join(spdl)+"\n")
    def run(self):
        while True:
            self.myspdtest()
            time.sleep(self.indenttime)


'''
def spdtest():                
    if os.path.exists("result/speedtest.json"):
        f=open('result/speedtest.json', "r+")
        f.truncate()
        speedtest.main(["--server","17223","--json","--share","--timeout","30"])
        with open("result/speedtest.json","r+") as spdresult:
            spdj = json.load(spdresult)
            print(spdj)
'''
if __name__ == "__main__":
    #ping测试列表
    pinglist = ["www.baidu.com","www.taobao.com","www.jd.com","www.google.com","111.11.11.11","8.8.8.8"]
    #开启一个ping测线程 间隔60sping一次
    pingthread1 = pingThread( pinglist, name = "任务-1")
    pingthread1.start()
    #开启一个测速线程 间隔900s测速一次
    speedtestthread1 = speedtestThread(nodeid = 17223, name = "任务-2")
    speedtestthread1.start()
    #pingthread1.join()
    #ping(pinglist)
    #myspdtest()
