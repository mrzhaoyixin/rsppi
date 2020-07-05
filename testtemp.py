import multiprocessing,time,threading,re,subprocess
class Pingclass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def write_file(self,result):
        print('zhaonb')
        try:
            s = ','.join(result)+'\n'
            #获取当前日期
            cudate = str(time.strftime("%Y-%m-%d", time.localtime()))
            with open('ping_'+'1111','a') as f:
                f.write(s)
        except Exception as e:
            print(e)
        
    def process(self,args,pcount="10", psize="32",timeout = "20"):
        print("pingtest", threading.current_thread().name)
        try:
            ip_address=args
            #print('get a addr ',ip_address,'remain ',self.q.qsize())
            p = subprocess.Popen(["ping", "-c", str(pcount), "-s", str(psize),"-W", str(timeout), ip_address], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
            #p = subprocess.call('ping -c 1 -w 1 '+ip_address, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            #print(p,'pdone')
            print('doing',args)
            out = p.stdout.read().decode('utf-8')
            #print('out',out)
            #with open("result/pingresulttemp","w+") as pingresult:
                #pingresult.write(out)
            reg_receive = '[0-9]* received'
            searchresult = re.search(reg_receive, out)
            #print(str(searchresult))
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
                        print([ip_address,domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate, 'success'])
                        #q.task_done()
                        resultlist_temp = [ip_address,domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate, 'success']
                        resultlist = [str(x) for x in resultlist_temp]
                        return resultlist
                    else:
                        targethost = out.split("\n")[0].split()[2][1:-1]
                        print("rttlist error:",rttlist)
                        resultlist_temp = [ip_address, targethost, targethost, "-",  "-",  "-",  "-",  "-",  'network fail']
                        resultlist = [str(x) for x in resultlist_temp]
                        return resultlist
                else:
                    print('网络不通，目标服务器不可达！')
                    targethost = out.split("\n")[0].split()[2][1:-1]
                    return [ip_address, targethost, targethost, "-",  "-",  "-",  "-",  "-",  'network fail']
            else:
                print("地址输入有错误",out)
                return [ip_address, ip_address, ip_address, "-",  "-",  "-",  "-",  "-", 'address error']
        except Exception as e:
            print(e)
    def run(self):
        print('bange')
        pool = multiprocessing.Pool(processes = 100)
        with open('pinglist.txt','r') as tasks:
            for t in tasks:
                #self.process(t[:-1])
                #break
                pool.apply_async(self.process, tuple(t[:-1]),callback=self.write_file)
                print('aaa')
                print(t)
                print('bbb')
                break
            pool.close()
            pool.join()

if __name__ == '__main__':
    wtt = Pingclass()
    wtt.start()