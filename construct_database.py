#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:33:21 2020

@author: gumenghan
"""

import time
from selenium import webdriver
from selenium.webdriver import ActionChains
import os
import sqlite3
import zipfile
from selenium.webdriver.firefox.options import Options
from collections import defaultdict
import operator
import re
import torch
import torchtext.vocab as vocab
import math
import torch.nn as nn
import torch.nn.functional as F #激励函数
import torch.utils.data as Data

def knn(W, x, k):
    #matmul 高维矩阵相乘
    #设置1e-10增加精确度
    cos = torch.matmul(W, x.view((-1,))) / ((torch.sum(W * W, dim=1) + 1e-10).sqrt() * torch.sum(x * x).sqrt())
    #topk 返回k个最大值
    _, topk = torch.topk(cos, k=k)
    topk = topk.cpu().numpy()
    return topk, [cos[i].item() for i in topk]


def get_similar_tokens(query, k, embed):
    topk, cos = knn(embed.vectors,embed.vectors[embed.stoi[query]], k+1)
    #zip 将对象打包，成为pair
    sim=[]
    for i, c in zip(topk[1:], cos[1:]): 
        #print('similarity=%.3f: %s' % (c, (embed.itos[i])))
        sim.append(embed.itos[i])
    return sim

#return the similarity of two words
def similar(W,x,embed):
    t1=embed.vectors[glove.stoi[W]]
    t2=embed.vectors[glove.stoi[x]]
    cos=sum(t1.mul(t2))/(sum(t1.mul(t1)).sqrt()*sum(t2.mul(t2)).sqrt())
    
    return cos



def download_glove(cache_dir):
    glove = vocab.GloVe(name='6B', dim=50, cache=cache_dir)
    return glove

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
            
#计算x和target集合里元素的相似度的均值
def mean_similar(x,target,glove):
    s=0
    for item in target:
        s=s+similar(item,x,glove)
    s=s/len(target)
    return s

#计算选取的词库内部总相似度(两两相似度之和)
def list_any_two_mul(mylist,glove):
     n=len(mylist)
     num = 1
     temp = []
     for i in mylist[:-1]:
         temp.append([similar(i,j,glove) for j in mylist[num:]])
         num = num + 1
     # 把多个列表变成只有一个列表
     results = [y for x in temp for y in x]
     #此处灿开kmeans算法k的取值
     return sum(results)/(n*(n-1)/math.sqrt(n))

def hier_cluster (n,WORDS,glove,target):
        #print(similar('finance', item, glove))
    
    SS=sorted(WORDS, key=lambda x: mean_similar(x, target, glove),reverse=True)
    SS=list(SS)
    return SS[n:],SS[:n],list_any_two_mul(SS[:n],glove)



# 从WORDS词汇库里选取100个金融词汇选取若干个词汇，构成金融词汇库，使得库内总相似度最大
# 神经网络算法
def construct_finance_database(n,target,WORDS,glove,limit):
    tmp=WORDS
    old_simi=0
    tmp,chosen,simi=hier_cluster(n, tmp, glove, target)
    simi=(int)(simi)
    stor=chosen
    while simi>old_simi & len(stor)<limit:
        old_simi=simi
        tmp,chosen,simi=hier_cluster(n, tmp, glove, stor)
        simi=(int)(simi)
        stor=stor+chosen
        stor=list(set(stor))
        #print(stor)
    return stor


class Encoder:
   Finance_words=['investment','foreign','banking','fund','government','treasury']
   def __init__(self, vector):
      self.v=vector
      self.values=vector
      self.ones=[]
      self.zeroes=[]
   def settle(self):
      for i in range(0,len(self.v)): 
          if self.v[i]==1:
              self.ones.append(Encoder.Finance_words[i])
          else:
              self.zeroes.append(i)
   def learn(self):
       if len(self.ones)>0:
           for item1 in self.zeroes:
               cal=mean_similar(Encoder.Finance_words[item1], self.ones, glove)
               self.values[item1]=cal
   def clean(self):
       for item in self.values:
           item=float(item)

       
       

if __name__=="__main__": 
    
    
    
    #############################################################################
    #####     PART 1     ######
    #############################################################################
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
        
    
    cu.execute('SELECT doc FROM TAG ')
    cx.commit()
    res=cu.fetchall()
    stor=[]
    Jarcoob=[]
    for i in range(1,len(res)):
        row=re.sub('[^\w+]', "\t", str(res[i]))
        stor.append(row.split('\t'))
        
    
    word_frequency=defaultdict(int)
    for row in stor:
        for i in row:
            word_frequency[i]+=1
    word_sort=sorted(word_frequency.items(),key=operator.itemgetter(1),reverse=True) #根据词频降序排序
    #选取出现次数最多的前一百个单词
    driver.quit()
    
    # if you have not downloaded, uncomment the following line
    cache_dir = "/Users/gumenghan/Datasets/tag1"
    download_glove(cache_dir)
    glove=download_glove(cache_dir)
    
    
    WORDS=[]
    count=0
    for item in word_sort:
        
        if (len(item[0])>=4):
            if (item[0] in list(glove.stoi)):
                
                WORDS.append(item[0].lower())
                count=count+1
        if (count==1000):
            break

    WORDS=list(set(WORDS))
    FINAL_OUTPUT=[]
    tmp=WORDS
    ##################
    target=['finance']
    ##################
    optimal=0
    index_chosen=0
    for i in range(2,10):
        start=time.time()
        GET=construct_finance_database(i,target,WORDS,glove,100)
        FINAL_OUTPUT.append(GET)
        end=time.time()
        #print(end-start)
        if len(GET)/(end-start)>optimal:
            optimal=len(GET)/(end-start)
            index_chosen=i
    
    #index_chosen
    FINAL_OUTPUT[index_chosen-2]
    
    finance_words=['investment','foreign','banking','fund','government','treasury']
    
    #############################################################################
    #####     PART 2     ######
    #############################################################################
    
    
    
    cu.execute('SELECT version FROM TAG ')
    res_version=cu.fetchall()
    cu.execute('SELECT custom FROM TAG ')
    res_custom=cu.fetchall()
    cu.execute('SELECT abstract FROM TAG ')
    res_abstract=cu.fetchall()
    cu.execute('SELECT datatype FROM TAG ')
    res_datatype=cu.fetchall()
    cu.execute('SELECT iord FROM TAG ')
    res_iord=cu.fetchall()
    cu.execute('SELECT crdr FROM TAG ')
    res_crdr=cu.fetchall()
    cx.commit()
    
    res_version_unique=list(set(res_version))
    
    #res_version和res_datatype 不用做Jarcard和clusterin，但需要保留
    #['investment',
    #'foreign',
    #'banking',
    #'fund',
    #'government',
    #'treasury']
    Jarcoob=[]
    for i in range(1,len(res)):
        row=re.sub('[^\w+]', "\t", str(res[i]))
        
        line=[]
        for item in finance_words:
            if item in row.split('\t'):
                line.append(1)
            else:
                line.append(0)
                
        line=list(line)
        #print(len(line))
        #print(len(finance_words))
        if len(line)==len(finance_words):
            Ec=Encoder(line);
            Ec.settle()
            Ec.learn()
            Ec.clean()
            Jarcoob.append(Ec.values)
            print(Ec.values)
        else:
            line=[0 for i in range(len(finance_words)) ]
            Jarcoob.append(line)
        
    Jarcoob
    #version: an identifier for the taxonomy; 
    #custom: 1 if tag is custom (version=adsh), 0 if it is standard
    #abstract: 1 if the tag is not used to represent a numeric fact
    #datatype: If abstract=1, then NULL, otherwise the data type (e.g., monetary) for the tag
    #Iord: If abstract=1, then NULL; otherwise, 
          #“I” if the value is a point-in time, or “D” if the value is a duration. 
    #crdr: If datatype = monetary, then the tag’s natural accounting balance (debit or credit); 
          #if not defined, then NULL. 
    
    #version 和 datatype 需要分类处理
    #custom,abstract,iord,crdr 只是0或者1
    #查看glove全部属性
    #dir(glove)
    #with cx:
        #cu.execute("SELECT * FROM TAG")
        #print(cu.fetchall())
    







