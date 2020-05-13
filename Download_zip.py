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


from selenium.webdriver.firefox.options import Options

options = Options()
options.set_preference("browser.download.folderList",2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir","/Users/gumenghan/Desktop/Data")
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel")
driver = webdriver.Firefox(firefox_options=options, executable_path = '/usr/local/bin/geckodriver')


driver.maximize_window()
driver.get('https://www.sec.gov/dera/data/financial-statement-data-sets.html')


pageSource = driver.page_source
print (pageSource)
ac=ActionChains(driver)
element=driver.find_elements_by_css_selector("a[href*='.zip']")
for i in range(0,len(element)):
    element[i].click()




driver.quit()
