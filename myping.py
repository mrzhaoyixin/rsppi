#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import re
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
            rttlist = rtt.split()[-2].split("/")
            min_time = rttlist[0]
            max_time = rttlist[1]
            avg_time = rttlist[2]
            lossrate = 1-int(receivepkg)/int(pcount)
            domain = out.split("\n")[0].split()[1]
            targethost = out.split("\n")[0].split()[2][1:-1]
            #目标主机 最小时延 最大时延 平均时延 收到包数量 丢包率 状态码
            return [domain, targethost, min_time, max_time, avg_time, receivepkg, lossrate, 0]
        else:
            print('网络不通，目标服务器不可达！')
            targethost = out.split("\n")[0].split()[2][1:-1]
            return [ip_address, targethost, "-",  "-",  "-",  "-",  "-", "-1"]
    else:
        print("地址输入有错误")
        return [ip_address, ip_address, "-",  "-",  "-",  "-",  "-", "-2"]
if __name__ == '__main__':
    print("ping start")
    arglist = sys.argv[1:]
    print("args:",arglist)
    for ip in arglist:
        print(get_ping_result(ip))
