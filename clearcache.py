#!/usr/bin/python3
# -*- coding: utf-8 -*-
import runtest, mytrace,speedtest,time,os,sys,json,threading,requests,onenet,config,subprocess,re,multiprocessing
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

global chrome_options
chrome_options = Options()
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')
#chrome_options.add_argument('--headless')
#chrome_options.add_argument("--remote-debugging-port=9222")
#chrome_options.add_argument("â€?incognito")
#chrome_options.add_argument('blink-settings=imagesEnabled=false')
#chrome_options.add_argument('--disable-gpu')
global driver
driver = webdriver.Chrome(executable_path = '/usr/bin/chromedriver', chrome_options = chrome_options)

driver.get('http://www.baidu.com')
cookies = driver.get_cookies()
print(f"main: cookies = {cookies}")
driver.delete_all_cookies()
cookies = driver.get_cookies()
print(f"main: cookies = {cookies}")
time.sleep(30)
driver.close()
#http://cn.voidcc.com/question/p-fenlakdk-hr.html