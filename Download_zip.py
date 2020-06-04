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
#####
            

    


if __name__=="__main__": 
    
    target_web='https://www.sec.gov/dera/data/financial-statement-data-sets.html'
    cwd = os.getcwd()
    options = Options()
    
    options.set_preference("browser.download.folderList",2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir",cwd)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    driver = webdriver.Firefox(firefox_options=options, executable_path = '/usr/local/bin/geckodriver')
    
    
    driver.maximize_window()
    
    driver.get(target_web)
    
    #driver.get('https://www.sec.gov/dera/data/financial-statement-data-sets.html')
    ##################  For Analysis of the Web Page  ##################
    #pageSource = driver.page_source
    ac=ActionChains(driver)
    #  Just a test for downloading one file  #
    driver.find_element_by_css_selector("a[href*='.zip']").click()
    
    
    ##################  For Downloading Multiple Files   ####################
    #element=driver.find_element_by_css_selector("a[href*='.zip']")
    #for i in range(0,len(element)):
    #    element[i].click()
    
    
    
    ##################  Create Database 'gmh1.db'  ####################
    ##################  Create table 'tag'  ####################
    cx = sqlite3.connect('./gmh1.db')
    cu = cx.cursor()
    cu.execute('''CREATE TABLE TAG
                 (tag, version, custom, abstract, datatype, iord, crdr, tlabel, doc)''')
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
        content=f.read()
        l=content.split('\n')
        for title in l:
            t=title.split('\t')
            if len(t)==9:
                cu.execute("INSERT INTO TAG(tag, version, custom, abstract, datatype, iord, crdr, tlabel, doc) VALUES (?,?,?,?,?,?,?,?,?)",(t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8]))
        
    cx.commit()
    
    with cx:
        cu.execute("SELECT * FROM TAG")
        print(cu.fetchall())
    driver.quit()
#with cx:
    #cu.execute("SELECT * FROM TAG")
    #print(cu.fetchall())





