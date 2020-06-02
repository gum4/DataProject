#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:33:21 2020

@author: gumenghan
"""

import time
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import pyautogui
import os
import sqlite3
import zipfile
from selenium.webdriver.firefox.options import Options


    
def un_zip(file_name):
    """unzip zip file"""
    zip_file = zipfile.ZipFile(file_name)
    if os.path.isdir(file_name + "_files"):
        pass
    else:
        os.mkdir(file_name + "_files")
    for names in zip_file.namelist():
        zip_file.extract(names,file_name + "_files/")
    zip_file.close()

def getFileName(path,N,special):

    f_list = os.listdir(path)
    for i in f_list:
        if os.path.splitext(i)[1] == special:
            N.append(i)

#os.chdir("/Users/gumenghan/Desktop/Spyder programs/try/Data_Project")
cwd = os.getcwd()
options = Options()
options.set_preference("browser.download.folderList",2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir",cwd)
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel")
driver = webdriver.Firefox(firefox_options=options, executable_path = '/usr/local/bin/geckodriver')


driver.maximize_window()
driver.get('https://www.sec.gov/dera/data/financial-statement-data-sets.html')
##################  For Analysis of the Web Page  ##################
#pageSource = driver.page_source
ac=ActionChains(driver)
#  Just a test for downloading one file  #
driver.find_element_by_css_selector("a[href*='.zip']").click()
N=[]
getFileName(cwd, N,'.zip')
for item in N:
    un_zip(item)
DIR=[]
getFileName(cwd, DIR,'.zip_files')
for item in DIR:
    #print(item)
    p=item+'/tag.txt'
    f=open(p)
    lines=f.readlines()
    for l in lines:
        print(l)
    
    
##################  For Downloading Multiple Files   ####################
#element=driver.find_element_by_css_selector("a[href*='.zip']")
#for i in range(0,len(element)):
#    element[i].click()

f=open('/Users/gumenghan/Desktop/Spyder programs/try//Data_Project/2020q1.zip_files/tag.txt')
content=f.read()
content.head()
l=content.split('\n')
k=0
for title in l:
    k=k+1
    t=title.split('\t')
    print((t))
    if k==100:
        break

segments=[]
for item in l:
    x=item.split('\t')
    for i in x:
        segments.append(i)
segments

cx = sqlite3.connect('./train.db')
cu = cx.cursor()
cu.execute('create table if not exists gmh1 (id integer primary key,name text)')


