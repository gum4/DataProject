#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 17:24:48 2020

@author: gumenghan
"""

import sqlite3
import torch
import os
import torchtext.vocab as vocab
import numpy
import re
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
    #zip 将对象打包
    sim=[]
    for i, c in zip(topk[1:], cos[1:]): 
        #print('similarity=%.3f: %s' % (c, (embed.itos[i])))
        sim.append(embed.itos[i])
    return sim


cache_dir = "/Users/gumenghan/Datasets/tag1"
# glove = vocab.pretrained_aliases["glove.6B.50d"](cache=cache_dir)
#下载glove数据
glove = vocab.GloVe(name='6B', dim=50, cache=cache_dir)
print(get_similar_tokens('hello', 5, glove))
cwd=os.getcwd()

cx = sqlite3.connect('./gmh1.db')
cu = cx.cursor()
cu.execute('SELECT doc FROM TAG ')
res=cu.fetchall()

row=re.sub('[^\w+]', "\t", str(res[1]))
stor=[]
for item in row.split('\t'):
    if item!='':
        stor.append(item)
        
stor
