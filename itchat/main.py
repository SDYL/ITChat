# -*- coding: utf-8 -*-
import csv
from typing import List

import jieba
import itchat
import os
import re
import time
import json
import base64
import requests
import sys
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from snownlp import SnowNLP
from pylab import *
from faceApi import FaceAPI
from PIL import Image
from jieba import analyse
from wordcloud import WordCloud

mpl.rcParams['font.sans-serif'] = ['SimHei']


def analyseSex(firends):
    sexs = list(map(lambda x: x['Sex'], friends[1:]))
    counts = Counter(sexs).items()
    counts = sorted(counts, key=lambda x: x[0], reverse=False)
    counts = list(map(lambda x: x[1], counts))
    labels = ['Unknow', 'Male', 'Female']
    colors = ['red', 'yellowgreen', 'lightskyblue']
    plt.figure(figsize=(8, 5), dpi=80)
    plt.axes(aspect=1)
    plt.pie(counts,
            labels=labels,
            colors=colors,
            labeldistance=1.1,
            autopct='%3.1f%%',
            shadow=False,
            startangle=90,
            pctdistance=0.6
            )
    plt.legend(loc='upper right', )
    plt.title(u'%s的微信好友性别组成' % friends[0]['NickName'])
    plt.show()


def analyseLocation(friends):
    freqs = {}
    headers = ['NickName', 'Province', 'City']
    with open('location.csv', 'w', encoding='utf-8', newline='', ) as csvFile:
        writer = csv.DictWriter(csvFile, headers)
        writer.writeheader()
        for friend in friends[1:]:
            row = {'NickName': friend['NickName'], 'Province': friend['Province'], 'City': friend['City']}
            if friend['Province'] is not None:
                if friend['Province'] not in freqs:

                    freqs[friend['Province']] = 1
                else:
                    freqs[friend['Province']] = 1
            writer.writerow(row)

    for (k, v) in freqs:
        print("{0}:{1}".format(k, v))


def analyseHeadImage(frineds):
    # Init Path
    basePath = os.path.abspath('.')
    baseFolder = basePath + '\\HeadImages\\'
    if not os.path.exists(baseFolder):
        os.makedirs(baseFolder)

    # Analyse Images
    faceApi = FaceAPI()
    use_face = 0
    not_use_face = 0
    image_tags = ''
    for index in range(1, len(friends)):
        friend = friends[index]
        # Save HeadImages
        imgFile = baseFolder + '\\Image%s.jpg' % str(index)
        imgData = itchat.get_head_img(userName=friend['UserName'])
        if not os.path.exists(imgFile):
            with open(imgFile, 'wb') as file:
                file.write(imgData)

        # Detect Faces
        time.sleep(1)
        result = faceApi.detectFace(imgFile)
        if result:
            use_face += 1
        else:
            not_use_face += 1

            # Extract Tags
        result = faceApi.extractTags(imgFile)
        image_tags += ','.join(list(map(lambda x: x['tag_name'], result)))

    labels = [r'使用人脸头像', u'不使用人脸头像']
    counts = [use_face, not_use_face]
    colors: list[str] = ['red', 'yellowgreen', 'lightskyblue']
    plt.figure(figsize=(8, 5), dpi=80)
    plt.axes(aspect=1)
    plt.pie(counts,  # 性别统计结果
            labels=labels,  # 性别展示标签
            colors=colors,  # 饼图区域配色
            labeldistance=1.1,  # 标签距离圆点距离
            autopct='%3.1f%%',  # 饼图区域文本格式
            shadow=False,  # 饼图是否显示阴影
            startangle=90,  # 饼图起始角度
            pctdistance=0.6  # 饼图区域文本距离圆点距离
            )
    plt.legend(loc='upper right', )
    plt.title(u'%s的微信好友使用人脸头像情况' % friends[0]['NickName'])
    plt.show()

    image_tags = image_tags.encode('iso8859-1').decode('utf-8')
    back_coloring = np.array(Image.open('face.jpg'))
    wordcloud = WordCloud(
        font_path='simfang.ttf',
        background_color="white",
        max_words=1200,
        mask=back_coloring,
        max_font_size=85,
        random_state=75,
        width=800,
        height=480,
        margin=15
    )

    wordcloud.generate(image_tags)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()


def analyseSignature(friends):
    signatures = ''
    emotions = []
    pattern = re.compile("1f\d.+")
    for friend in friends:
        signature = friend['Signature']
        if signature is not None:
            signature = signature.strip().replace('span', '').replace('class', '').replace('emoji', '')
            signature = re.sub(r'1f(\d.+)', '', signature)
            if len(signature) > 0:
                nlp = SnowNLP(signature)
                emotions.append(nlp.sentiments)
                signatures += ' '.join(jieba.analyse.extract_tags(signature, 5))
    with open('signatures.txt', 'wt', encoding='utf-8') as file:
        file.write(signatures)

    # Sinature WordCloud
    back_coloring = np.array(Image.open('flower.jpg'))
    wordcloud = WordCloud(
        font_path='simfang.ttf',
        background_color="white",
        max_words=1200,
        mask=back_coloring,
        max_font_size=75,
        random_state=45,
        width=960,
        height=720,
        margin=15
    )

    wordcloud.generate(signatures)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.show()
    wordcloud.to_file('signatures.jpg')

    # Signature Emotional Judgment
    count_good = len(list(filter(lambda x: x > 0.66, emotions)))
    count_normal = len(list(filter(lambda x: 0.33 <= x <= 0.66, emotions)))
    count_bad = len(list(filter(lambda x: x < 0.33, emotions)))
    print(count_good * 100 / len(emotions))
    print(count_normal * 100 / len(emotions))
    print(count_bad * 100 / len(emotions))
    labels = [u'负面消极', u'中性', u'正面积极']
    values = (count_bad, count_normal, count_good)
    plt.rcParams['font.sans-serif'] = ['simHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.xlabel(u'情感判断')
    plt.ylabel(u'频数')
    plt.xticks(range(3), labels)
    plt.legend(loc='upper right', )
    plt.bar(range(3), values, color='rgb')
    plt.title(u'%s的微信好友签名信息情感分析' % friends[0]['NickName'])
    plt.show()


# login wechat and extract friends
itchat.auto_login(hotReload=True)
friends = itchat.get_friends(update=True)
analyseSex(friends)
analyseSignature(friends)
analyseHeadImage(friends)
analyseLocation(friends)
