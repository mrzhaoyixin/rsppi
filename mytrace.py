#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os,sys,time,subprocess
import warnings,logging

warnings.filterwarnings("ignore",category=DeprecationWarning)
logging.getLogger("scapy.runtine").setLevel(logging.ERROR)

from scapy.as_resolvers import AS_resolver_radb 
from scapy.all import traceroute

def get_trace_result(domain,dport=[80,443], timeout=2, minttl=1, maxttl=30):
    tempstdout=sys.stdout
    file = open("result/traceresult.txt", "w+")
    sys.stdout = file
    res,unans = traceroute(domain, dport=dport, timeout=timeout, minttl=minttl, maxttl=maxttl)
    res.graph(target = "> result/trace.svg",  ASres=AS_resolver_radb(), type="svg")
    file.flush()
    sys.stdout=tempstdout
    file.close()
    return res,unans
