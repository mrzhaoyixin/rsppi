#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import subprocess
import re
def get_speedtest_result(nodeid):
	if nodeid is None:
		p = subprocess.Popen(["speedtest",  "--format=json"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
		out = p.stdout.read().decode('utf-8')
		return out
	else:
		p = subprocess.Popen(["speedtest", "--server-id", str(nodeid), "--format=json"], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = False)
		out = p.stdout.read().decode('utf-8')
		return out
