#!/usr/bin/python
# -*- coding: utf-8 -*-
#Постобработка газет
import os, re, codecs, shutil, random
requestedWordAmount = input(u'Введите желаемое количество словоупотреблений: ')
periodStartYear = 2013
periodStartMonth = 01
periodEndYear = 2013
periodEndMonth = 12
period = []

#Обработка периода; по каким папкам надо будет ходить
for i in range(periodStartYear, periodEndYear + 1):
    for j in range(periodStartMonth, periodEndMonth + 1):
        if j < 10:
            period.append('izvestia\\' + str(i) + '\\0' + str(j))
        else:
            period.append('izvestia\\' + str(i) + '\\' + str(j))

#Создаем папку results
newPath = os.curdir + '/results/'
if not os.path.exists(newPath):
    os.makedirs(newPath)

#Узнаем количество папок, создаем словари первого уровня
folders = {}
for root, dirs, files in os.walk('izvestia'):
    for i in files:
        if os.path.split(os.path.join(root, i))[0] in period:
            folders[os.path.split(os.path.join(root, i))[0]] = {}

#Узнаем среднее количество слов в папке
averagePerFolder = requestedWordAmount/len(folders)
print u'Папок в рассматриваемом периоде: ' + str(len(folders))
print u'Среднее количество слов в папке: ' + str(averagePerFolder)

#Ищем wordcount в документах, создаем словари второго уровня
for root, dirs, files in os.walk('izvestia'):
    for i in files:
        if os.path.split(os.path.join(root, i))[0] in period:
            f = codecs.open(os.path.join(root, i), 'r', 'utf-8')
            text = f.read()
            f.close()
            searchWordcount = re.search(u'<WORDCOUNT>([0-9]*)</WORDCOUNT>', text)
            if searchWordcount != None:
                folders[os.path.split(os.path.join(root, i))[0]][os.path.join(root, i)] = int(searchWordcount.group(1))

#Копируем нужные файлы
wordsInFolder = 0
wordsAllFolders = 0
usedKeys = []
for i in folders:
    for j in folders[i]:
        wordsInFolder = wordsInFolder + folders[i][j]
    wordsAllFolders = wordsAllFolders + wordsInFolder

if wordsAllFolders < requestedWordAmount:
    print u'За данный период невозможно собрать запрошенное число слов'
else:
    for i in folders:
        if wordsInFolder > averagePerFolder:
            currentWordcount = 0
            for j in folders[i]:
                randomFile = random.choice(folders[i].keys())
                if folders[i][randomFile] < 300:
                    while folders[i][randomFile] < 300:
                        randomFile = random.choice(folders[i].keys())
                if randomFile not in usedKeys:
                    currentWordcount = currentWordcount + int(folders[i][randomFile])
                    if currentWordcount < averagePerFolder:
                            if not os.path.exists(newPath + i):
                                os.makedirs(newPath + i)
                            shutil.copy2(randomFile, newPath + randomFile)
                            usedKeys.append(randomFile)
        else:
            currentWordcount = currentWordcount + int(folders[i][j])
            if currentWordcount < averagePerFolder:
                if folders[i][j] > 300:
                    if not os.path.exists(newPath + i):
                        os.makedirs(newPath + i)
                    shutil.copy2(j, newPath + j)

#Тестируем, что получили в папке results
totalAmount = 0
for root, dirs, files in os.walk('results'):
    for i in files:
            f = codecs.open(os.path.join(root, i), 'r', 'utf-8')
            text = f.read()
            f.close()
            searchWordcount = re.search(u'<WORDCOUNT>([0-9]*)</WORDCOUNT>', text)
            if searchWordcount != None:
                print u'Файл размером: ' + searchWordcount.group(1)
                totalAmount = totalAmount + int(searchWordcount.group(1))
print u'Всего слов: ' + str(totalAmount)
