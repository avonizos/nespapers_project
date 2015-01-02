# !/usr/bin/python
#  -*- coding: utf-8 -*-

import os
import re
import codecs
import shutil
import random
import sys

# Input string example:
# python.exe postediting.py 100000 2012 10 2013 10 izvestia

period = []
folders = {}
new_path = os.path.join(os.path.dirname(__file__), 'results')


# Which folders will be used
def eval_period(period_start_year, period_start_month, period_end_year, period_end_month, domain):
    if period_start_year == period_end_year:
        for j in range(period_start_month, period_end_month + 1):
            if j < 10 and str(j)[0] != 0:
                period.append(os.path.join(os.path.dirname(__file__), domain) +
                              '\\' + str(period_start_year) + '\\0' + str(j))
            else:
                period.append(os.path.join(os.path.dirname(__file__), domain) +
                              '\\' + str(period_start_year) + '\\' + str(j))
    else:
        for i in range(period_start_year, period_end_year + 1):
            if i == period_start_year:
                cur_start_month = period_start_month
                cur_end_month = 12
            elif i == period_end_year:
                cur_start_month = 1
                cur_end_month = period_end_month
            else:
                cur_start_month = 1
                cur_end_month = 12
            for j in range(cur_start_month, cur_end_month + 1):
                if j < 10:
                    period.append(os.path.join(os.path.dirname(__file__), domain) + '\\' + str(i) + '\\0' + str(j))
                else:
                    period.append(os.path.join(os.path.dirname(__file__), domain) + '\\' + str(i) + '\\' + str(j))
        # Create results folder
            if not os.path.exists(new_path):
                os.makedirs(new_path)


# Count amount of folders, create dictionaries of the first level
def count_dirs(domain):
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), domain)):
        for i in files:
            if os.path.split(os.path.join(root, i))[0] in period:
                folders[os.path.split(os.path.join(root, i))[0]] = {}
    print u'Folders in the requested period: ' + str(len(folders))


# Count average amount of words per folder
def count_average(requested_word_amount):
    average_per_folder = requested_word_amount/len(folders)
    return average_per_folder


# Search wordcount in documents, create dictionaries of the second level
def find_wordcount(domain):
    print u'Average amount of words per folder: ' + str(count_average(int(sys.argv[1])))
    for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), domain)):
        for i in files:
            if os.path.split(os.path.join(root, i))[0] in period:
                f = codecs.open(os.path.join(root, i), 'r', 'utf-8')
                text = f.read()
                f.close()
                search_wordcount = re.search(u'<WORDCOUNT>([0-9]*)</WORDCOUNT>', text)
                if search_wordcount is not None:
                    folders[os.path.split(os.path.join(root, i))[0]][os.path.join(root, i)] = int(search_wordcount.group(1))


# Copy files
def copy_files(requested_word_amount):
    words_in_folder = 0
    words_all_folders = 0
    used_keys = []
    for i in folders:
        for j in folders[i]:
            words_in_folder = words_in_folder + folders[i][j]
        words_all_folders += words_in_folder
    if words_all_folders < requested_word_amount:
        print u'Not enough words in the requested period'
    else:
        for i in folders:
            current_wordcount = 0
            if words_in_folder > count_average(int(sys.argv[1])):
                for j in folders[i]:
                    random_file = random.choice(folders[i].keys())
                    if folders[i][random_file] < 300:
                        while folders[i][random_file] < 300:
                            random_file = random.choice(folders[i].keys())
                    if random_file not in used_keys:
                        current_wordcount += int(folders[i][random_file])
                        if current_wordcount < count_average(int(sys.argv[1])):
                                if not os.path.exists(new_path + '\\' +
                                                      os.path.basename(os.path.dirname(os.path.dirname(i))) + '\\' +
                                                      os.path.basename(os.path.dirname(i)) + '\\' +
                                                      os.path.basename(i)):
                                    os.makedirs(new_path + '\\' +
                                                os.path.basename(os.path.dirname(os.path.dirname(i))) + '\\' +
                                                os.path.basename(os.path.dirname(i)) + '\\' + os.path.basename(i))
                                shutil.copy2(random_file,  new_path + '\\' +
                                             os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(random_file)))) + '\\' +
                                             os.path.basename(os.path.dirname(os.path.dirname(random_file))) + '\\' +
                                             os.path.basename(os.path.dirname(random_file)) + '\\' +
                                             os.path.basename(random_file))
                                print u'Words in the file copied: ' + str(folders[i][random_file])
                                used_keys.append(random_file)
            else:
                current_wordcount += int(folders[i][j])
                if current_wordcount < count_average(int(sys.argv[1])):
                    if folders[i][j] > 300:
                        if not os.path.exists(new_path + '\\' +
                                              os.path.basename(os.path.dirname(os.path.dirname(i))) + '\\' +
                                              os.path.basename(os.path.dirname(i))):
                            os.makedirs(new_path + '\\' +
                                        os.path.basename(os.path.dirname(os.path.dirname(i))) + '\\' +
                                        os.path.basename(os.path.dirname(i)))
                        shutil.copy2(j, new_path + '\\' +
                                     os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(j)))) + '\\' +
                                     os.path.basename(os.path.dirname(os.path.dirname(j))) + '\\' +
                                     os.path.basename(os.path.dirname(j)) + os.path.basename(j))
                        print u'Words in the file copied: ' + str(folders[i][j])
            print u'Total amount: ' + str(current_wordcount)


def main():
    eval_period(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    count_dirs(sys.argv[6])
    count_average(int(sys.argv[1]))
    find_wordcount(sys.argv[6])
    copy_files(int(sys.argv[1]))

if __name__ == "__main__":
    main()