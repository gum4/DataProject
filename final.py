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
#from selenium.webdriver.firefox.options import Options
from collections import defaultdict
import operator
import re
import torch
import torchtext.vocab as vocab
import math
import numpy as np
import sys
from scipy import stats
import pandas as pd
from time import sleep

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

########################   以下没有用到   ############################
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

########################   以上没有用到   ############################
           
def mydist(p1, p2):
    union=list(p1 | p2)
    cross=list(p1 & p2)
    num1=cross.count(True)
    num2=union.count(True)
    if num2==0:
        return 0
    return 1-num1/num2


def hierarchial_select (J):

    min_dis=2
    index1=-1
    index2=-1
    #result=[]
    for i in range(0,len(J)):
        remain=np.delete(J,i,axis=0)
        select=sorted(remain, key=lambda x: mydist(x,J[i]),reverse=False)
        if mydist(select[0],J[i])<min_dis:
            min_dis=mydist(select[0],J[i])
            index1=i
            #all(axis==1)表示某一行的所有列
            index2=np.where((J == select[0]).all(axis=1))
            #result=select[0]
    cluster=np.array([J[index1],J[(int)(index2[0])]])
    J1=np.delete(J,[index1,(int)(index2[0])],axis=0)
    J2=np.insert(J1, 0, values=cluster_mean(cluster), axis=0)
    J2=np.unique(J2, axis=0)
    #cluster表示每次选出的两个，J1表示除去选出的两类剩下的，J2表示J1加上了一个mean_cluster
    return J[index1],J[(int)(index2[0])],J2,cluster_mean(cluster)


def cluster_mean(cluster):
    res=[]
    for i in range(cluster.shape[1]):
        counts = np.bincount(cluster[:,i])
        res.append(np.argmax(counts))
    return res

#融合过程，每一次iteration选出来的两类的mean，加紧j，unique后再被选出来，只需要看该组合在初始的J中的位置来选即可
#即选取某一类的组合等价于从原来的J中选值和mean相等的元素
def hierarchial_clustering (J,n):
    j=J
    classes=[]
    num_of_class=len(J)
    while num_of_class>n+1:
        c1,c2,j,m=hierarchial_select(j)
        classes.append([(int)(np.where((J == c1).all(axis=1))[0]),(int)(np.where((J == c2).all(axis=1))[0]),(int)(np.where((J == m).all(axis=1))[0])])
        num_of_class=num_of_class-1
    
    return classes
#L[2]和L[0]或L[1]相等,自己消化
#否则用L[2]在其他里面找
def hierarchical (L):
    RES=[]
    R=[]
    for row in L:
        RES.append(row[:][0:2])
    for i in range(0,len(L)):
        #if (L[i][2]==L[i][0]) | (L[i][2]==L[i][1]):
            #continue
        TMP=RES
        tmp=RES[i]
        RES[i]=[]
        inside=False
        for item in RES:
            if item==[]:
                continue
            if (item[0]==L[i][0]) | (item[1]==L[i][0]) | (item[0]==L[i][1]) | (item[1]==L[i][1]) | (item[0]==L[i][2]) | (item[1]==L[i][2]) :
                inside=True
                tmp.extend((list)(item))
                #item.append(L[i][0:2])
                item=[]
        #RES[i]=tmp
        R.append((list)((set)(tmp)))
        if inside==False:
            RES=TMP
    
    for i in range (0,len(R)):
        if R[i]==[]:
            continue
        for j in range (0,len(R)):
            if (R[j]==[]) | (i==j):
                continue
            set_c = set(R[i]) & set(R[j])
            list_c = list(set_c)
            if list_c!=[]:
                
                R[i].extend((list)(R[j]))
                R[j]=[]
        
        R[i]=(list)((set)(R[i]))
    R=[x for x in R if x]
    return R



    
def new_text_transfer(txt_file, Words,finance_words):
    f=open(txt_file)
    content=f.read()
    l=content.split('\n')
    output=[]
    for word in Words:
        inside=False
        for row in l:
            for i in word:
                if i in row.lower():
                    inside=True
                    break
        if inside:
            output.append(1)
        else:
            output.append(0)
    for item in finance_words:
        inside=False
        for row in l:
            if item in row.lower():
                inside=True
                break
        if inside:
            output.append(1)
        else:
            output.append(0)
    return output


if __name__=="__main__": 
    
    
    
    #############################################################################
    #####     PART 1     ######
    #############################################################################
    target_web='https://www.sec.gov/dera/data/financial-statement-data-sets.html'
    os.chdir('/Users/gumenghan/Desktop/Spyder programs/try/Data_project')
    sub_dir='data_collection'
    os.mkdir(sub_dir)
    cwd = os.getcwd()
    profile = webdriver.FirefoxProfile()

    profile.set_preference("browser.download.folderList",2)
    #profile.set_preference("browser.download.manager.showWhenStarting", False)
    #profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference("browser.download.dir",cwd+'/'+sub_dir)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
"application/zip,text/plain,application/vnd.ms-excel,text/csv,text/comma-separated-values,application/octet-stream,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document");
    driver = webdriver.Firefox(firefox_profile=profile, executable_path = '/usr/local/bin/geckodriver')
    
    
    driver.maximize_window()
    
    driver.get(target_web)
    
    #driver.get('https://www.sec.gov/dera/data/financial-statement-data-sets.html')
    ##################  For Analysis of the Web Page  ##################
    #pageSource = driver.page_source
    
    driver.page_source
    ac=ActionChains(driver)
    #  Just a test for downloading one file  #
    #driver.find_element_by_css_selector("a[href*='.zip']").click()
    #sleep(3)    
    
    ##################  For Downloading Multiple Files   ####################
    element=driver.find_elements_by_css_selector("a[href*='.zip']")
    count=0
    i=0
    while i<len(element):
        if count==1:
            break
        element[i].click()
        count=count+1
        i=i+4
    sleep(10)
    
    ##################  Create Database 'gmh1.db'  ####################
    ##################  Create table 'tag'  ####################
    cx = sqlite3.connect('./gmh1.db')
    cu = cx.cursor()
    cu.execute('''CREATE TABLE TAG
                 (tag, version, custom, abstract, datatype, iord, crdr, tlabel, doc)''')
    N=[]
    getFileName(cwd+'/'+sub_dir, N,'.zip')

    for item in N:
        un_zip(sub_dir+'/'+item)
    DIR=[]
    getFileName(cwd+'/'+sub_dir, DIR,'.zip_files')
    for item in DIR:
        p=sub_dir+'/'+item+'/tag.txt'
        if os.path.exists(p):
            
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
    #FINAL_OUTPUT[index_chosen-2]
    
    finance_words=FINAL_OUTPUT[index_chosen-2]
    #finance_words
    
    #############################################################################
    #####     PART 2     ######
    #############################################################################
    
    cu.execute('SELECT tag FROM TAG ')
    res_tag=cu.fetchall()
    
    
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
    #Jarcoob 中某个纬度上是1表示确定存在证据证实该唯独的信息存在
    Jarcoob=[]
    
    for i in range(1,len(res)):
        row=re.sub('[^\w+]', "\t", str(res[i]))
        
        line=[]
        line.append(True if res_custom[i]==('1',) else False)
        line.append(True if res_abstract[i]==('1',) else False)
        # point-in and credit is 1 
        line.append(True if res_iord[i]=='I' else False)
        line.append(True if res_crdr[i]=='C' else False)
        for item in finance_words:
            if item in row.split('\t'):
                line.append(True)
            else:
                line.append(False)
                
        line=list(line)
        Jarcoob.append(line)
        #if len(line)==len(finance_words):
            #Ec=Encoder(line);
            #Ec.settle()
            #Ec.learn()
            #Ec.clean()
            #Jarcoob.append(Ec.values)
            #print(Ec.values)
        #else:
            #line=[0 for i in range(len(finance_words)) ]
            #Jarcoob.append(line)

    #pd1=pd.DataFrame(Jarcoob,columns=['custom','abstract','iord','crdr','finance','investment','financial','foreign','banking','fund','government','treasury'])
    J=np.array(Jarcoob)
    
    unique_J=np.unique(J, axis=0)
    NUM_OF_CLASSES=5
    hier=hierarchial_clustering(unique_J,NUM_OF_CLASSES)
    R=hierarchical(hier)

    ################   R为最终分类   ################
    #print(R)
    
    #pd1.drop([1,2,3,4], axis=0)
    #version: an identifier for the taxonomy; 
    #custom: 1 if tag is custom (version=adsh), 0 if it is standard   ##########
    #abstract: 1 if the tag is not used to represent a numeric fact   ##########
    #datatype: If abstract=1, then NULL, otherwise the data type (e.g., monetary) for the tag
    #Iord: If abstract=1, then NULL; otherwise, 
          #“I” if the value is a point-in time, or “D” if the value is a duration. 
        ########
    #crdr: If datatype = monetary, then the tag’s natural accounting balance (debit or credit); 
          #if not defined, then NULL. 
        ########
    #version 和 datatype 需要分类处理
    #custom,abstract,iord,crdr 只是0或者1
    #查看glove全部属性
    #dir(glove)
    #with cx:
        #cu.execute("SELECT * FROM TAG")
        #print(cu.fetchall())
    


    #############################################################################
    #####     PART 3     ######
    #############################################################################
    
    
    predict_mean=[]
    for i in range(0,len(R)):
        predict_mean.append(cluster_mean(unique_J[R[i]]))
    
    
    words_for_use=['custom','numeric','point','monetary']
    Words=[]
    for item in words_for_use:
        Words.append(get_similar_tokens(item,10,glove))

    #####    predict_mean存储每一个cluster的mean  ######
    #####    下面计算新给出一篇新文本，其在给定维度上是什么   #####
    new_input=new_text_transfer(sys.argv[1],Words,finance_words)  
    MIN_DIST_index=-1
    MIN_DIST=1
    for i in range(0,len(predict_mean)):
        if mydist(np.array(new_input), np.array(predict_mean[i]))<MIN_DIST:
            MIN_DIST=mydist(np.array(new_input), np.array(predict_mean[i]))
            MIN_DIST_index=i
    #####    MIN_DIST_index表示这篇pdf应该被划分在这个位置   #####
    #MIN_DIST_index
    
    #############################################################################
    #####     PART 4     ######
    #############################################################################
    pre=[]
    for item in predict_mean[MIN_DIST_index]:
        if item==1:
            pre.append(True)
        else:
            pre.append(False)
    #####  PRE记录J中值等于 #####
    PRE=np.where((J == pre).all(axis=1))[0]
    RES_TAG=np.array(res_tag)[PRE]
    RES_VERSION=np.array(res_version)[PRE]
    target_tag=stats.mode(RES_TAG)[0][0][0]
    target_version=stats.mode(RES_VERSION)[0][0][0]
    ##################  Create table PRE & NUM  ####################
    #cu.execute('''DROP TABLE NUM''')
    #cx.commit()

    cu.execute('''CREATE TABLE NUM
                 (adsh, tag, version, ddate, qtrs, uom, coreg, value, footnote)''')
    
    cu.execute('''CREATE TABLE PRE
                 (adsh, report, line, stmt, inpth, rfile, tag, version, plabel, negating)''')
    
    #  use variable ###tag & version### to locate the targets in PRE and NUM datasets   #
    ########################             
    #  grab report
    for item in DIR:
        #print(item)
        p=sub_dir+'/'+item+'/pre.txt'
        if os.path.exists(p):
            f=open(p)
            content=f.read()
            l=content.split('\n')
            for title in l:
                t=title.split('\t')
                if len(t)==10:
                    cu.execute("INSERT INTO PRE(adsh, report, line, stmt, inpth, rfile, tag, version, plabel,negating) VALUES (?,?,?,?,?,?,?,?,?,?)",(t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8],t[9]))
    
    for item in DIR:
        #print(item)
        p=sub_dir+'/'+item+'/num.txt'
        if os.path.exists(p):
            f=open(p)
            content=f.read()
            l=content.split('\n')
            for title in l:
                t=title.split('\t')
                if len(t)==9:
                    cu.execute("INSERT INTO NUM(adsh, tag, version, ddate, qtrs, uom, coreg, value, footnote) VALUES (?,?,?,?,?,?,?,?,?)",(t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],t[8]))
    
    
    NUM_dataset=cu.execute('SELECT * FROM NUM ').fetchall()
    PRE_dataset=cu.execute('SELECT * FROM PRE ').fetchall()
    cx.commit()
    NUM_pd = pd.DataFrame(NUM_dataset[1:], columns =NUM_dataset[0]) 
    PRE_pd = pd.DataFrame(PRE_dataset[1:], columns =PRE_dataset[0]) 
    NUM_select=NUM_pd.loc[(NUM_pd['tag']==target_tag) & (NUM_pd['version']==target_version)]
    
    PRE_select=PRE_pd.loc[(PRE_pd['tag']==target_tag) & (PRE_pd['version']==target_version)]
    
    
    #### NUM dataset ####
    DDATE=[]  #The end date for the data value, rounded to the nearest month end.
    QTRS=[]#The count of the number of quarters represented by the data value, rounded to the nearest whole number. “0” indicates it is a point-in-time value.
    UOM=[] #The unit of measure for the value.
    COREG=[] #If specified, indicates a specific co-registrant, the parent company, or other entity (e.g., guarantor).  NULL indicates the consolidated entity.
    VALUE=[] #The value. This is not scaled, it is as found in the Interactive Data file, but is limited to four digits to the right of the decimal point. 
    FOOTNOTE=[] #The text of any superscripted footnotes on the value
    
    #### PRE dataset ####
    STMT=[] #The financial statement location to which the value of the “report field pertains
    PLABEL=[] #The text presented on the line item, also known as a “preferred” label.
    
    VERSION=[]
    TAG=[]
    
    for index, row in NUM_select.iterrows():
        item=PRE_select.loc[PRE_select['adsh']==row['adsh']]
        
        if len(item)>0:
            item=item.iloc[0]
            DDATE.append(row['ddate'])
            QTRS.append(row['qtrs'])
            UOM.append(row['uom'])
            COREG.append(row['coreg'])
            VALUE.append(row['value'])
            FOOTNOTE.append(row['footnote'])
            VERSION.append(row['version'])
            TAG.append(row['tag'])
            
            STMT.append(str(item['stmt'][1:]))
            PLABEL.append(str(item['plabel'][1:]))
    
    F = open('output.txt','w')
    F.write('TAG:   The unique identifier (name) for a tag in a specific taxonomy release.\n')
    F.write('VERSION:   The taxonomy identifier if the tag is a standard tag.\n')
    F.write('DDATE:   The end date for the data value, rounded to the nearest month end.\n')
    F.write('QTRS:   The count of the number of quarters represented by the data value, rounded to the nearest whole number. “0” indicates it is a point-in-time value.\n')
    F.write('UOM:   The unit of measure for the value.\n')
    F.write('COREG:   If specified, indicates a specific co-registrant, the parent company, or other entity (e.g., guarantor).  NULL indicates the consolidated entity.\n')
    F.write('VALUE:   The value. This is not scaled, it is as found in the Interactive Data file, but is limited to four digits to the right of the decimal point. \n')
    F.write('FOOTNOTE:   The text of any superscripted footnotes on the value.\n')
    F.write('STMT:   The financial statement location to which the value of the “report field pertains.\n')
    F.write('PLABEL:   The text presented on the line item, also known as a “preferred” label.\n')
    F.write('\n')
    F.write('\n')
    F.write('\n')
    F.write('\n')
    F.write('\n')
    for i in range(1,len(TAG)):
        string1='TAG: '+TAG[i]+';   VERSION: '+VERSION[i]+';   DDATE:'+DDATE[i]+';   QTRS:'+QTRS[i]
        F.write(string1)
        F.write('\n')
        string2='UOM: '+UOM[i]+';   COREG: '+COREG[i]+';   VALUE:'+VALUE[i]+';   FOOTNOTE:'+FOOTNOTE[i]
        F.write(string2)
        F.write('\n')
        string3='STMT: '+STMT[i]+';   PLABEL: '+PLABEL[i]
        F.write(string3)
        F.write('\n')
        F.write('\n')