#! /usr/bin/python3
# -*- coding: utf-8 -*-
import pandas as pd
import os
from re import sub, findall
from multiprocessing.dummy import Pool as ThreadPool
import codecs
from datetime import datetime
from collections import Counter

# Зчитуємо файл з метаданими дисертацій
df = pd.read_excel('DisserData.xlsx')

# Відбираємо дисертації із соціології
soccounter=[]
def checkSociology(i):
    keywords="соц.н.|соціологічних наук"
    degree=str(df["degree_code"][i])
    if len(findall(keywords, degree))>0:
        return "Соціолог"
    else:
        return "Несоціолог"

pool = ThreadPool(50)
socestimate=pool.map(checkSociology, [i[0] for i in enumerate(df["degree_code"])])
df["Sociology estimate"]=socestimate
df2=df.loc[df["Sociology estimate"] == "Соціолог"]

# Додаємо тексти анотацій за реєстраційним номером дисертації
texts=[]
for i in df2["reg_num"]:
    try:
        with codecs.open(f'texts/{i}.txt', encoding="utf-8") as file:
            data = file.read().replace('\n', ' ')
            texts.append(data)
    except:
        texts.append("")

df2["Texts"]=texts

# Відбираємо слова, написані з великої літери
def cleanText(i):
    t = sub("@\w+ ?", ' ', i)
    t = sub("[^\w\s]|[\d]", ' ', t)
    t = sub("\s+", ' ', t)
    return t

def findCapitals(i):
    words=[]
    try:
        text = cleanText(df2["title"][i])+" "+cleanText(df2["Texts"][i])
        if len(text.split())>0:
            for w in text.split()[1:]:
                if w[0].isupper():
                    words.append(w)
    except:
        pass
    return words

pool = ThreadPool(50)
words=pool.map(findCapitals, [i[0] for i in enumerate(df2["title"])])
df2["Capital words"]=words

# Підраховуємо частоти слів з великої літери по роках
dates=[datetime.strptime(str(i), '%Y%m%d') for i in df2["defense_date"]]
df2["Dates"]=dates

words1990s=[]
words2000s=[]
words2010s=[]
counter1990s=0
counter2000s=0
counter2010s=0
for i in enumerate(df2["Texts"]):
    try:
        if df2["Dates"][i[0]].year<2000:
            counter1990s+=1
            words1990s.extend(df2["Capital words"][i[0]])
        elif df2["Dates"][i[0]].year < 2010:
            counter2000s+=1
            words2000s.extend(df2["Capital words"][i[0]])
        elif df2["Dates"][i[0]].year < 2020:
            counter2010s+=1
            words2010s.extend(df2["Capital words"][i[0]])
        else:
            pass
    except:
        pass



def most_frequent(List):
    occurence_count = Counter(List)
    return occurence_count.most_common()

# Виводимо кількість дисертацій 2010х років та частоти слів з великої літери за спаданням
# Далі аналіз вручну, оскільки імена можуть мати різне написання і треба бути "в контексті"
print(counter2010s)
print(most_frequent(words2010s))