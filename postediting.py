# !/usr/bin/python
#  -*- coding: utf-8 -*-

import os
import re
import codecs
import shutil
import random
import sys
import newspapers


# Input string example:
# python.exe postediting.py 100000 2012 10 2013 10 izvestia

new_path = os.path.join(os.path.dirname(__file__), 'results')


class Newspaper:
    def __init__(self):
        self.domain = ''
        self.period = []
        self.folders = {}
        self.average_per_folder = 0
        self.words_copied = 0

    # Which folders will be used
    def eval_period(self, period_start_year, period_start_month, period_end_year, period_end_month, domain):
        if period_start_year == period_end_year:
            for j in range(period_start_month, period_end_month + 1):
                self.period.append(os.path.join(os.path.dirname(__file__),
                                                domain, str(period_start_year), str(j)))
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
                        month_str = '0' + str(j)
                    else:
                        month_str = str(j)
                    self.period.append(os.path.join(os.path.dirname(__file__), domain, str(i), month_str))
            # Create results folder
                if not os.path.exists(new_path):
                    os.makedirs(new_path)

    # Count amount of folders, create dictionaries of the first level
    def count_dirs(self, domain):
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), domain)):
            for i in files:
                if os.path.split(os.path.join(root, i))[0] in self.period:
                    self.folders[os.path.split(os.path.join(root, i))[0]] = {}
        print u'Folders in the requested period: ' + str(len(self.folders))

    # Count average amount of words per folder
    def count_average(self, requested_word_amount):
        self.average_per_folder = requested_word_amount/len(self.folders)

    # Search wordcount in documents, create dictionaries of the second level
    def find_wordcount(self, domain):
        print u'Average amount of words per folder: ' + str(self.average_per_folder)
        for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__), domain)):
            for i in files:
                if os.path.split(os.path.join(root, i))[0] in self.period:
                    f = codecs.open(os.path.join(root, i), 'r', 'utf-8')
                    text = f.read()
                    f.close()
                    search_wordcount = re.search(u'<WORDCOUNT>([0-9]*)</WORDCOUNT>', text)
                    if search_wordcount is not None:
                        self.folders[os.path.split(os.path.join(root, i))[0]][os.path.join(root, i)] =\
                            int(search_wordcount.group(1))

    # Copy files
    def copy_files(self, domain, requested_word_amount, actual_word_amount): # Function for copying files
        words_all_folders = 0 # Amount of words in all folders in the requested period
        for i in self.folders:
            for j in self.folders[i]:
                words_all_folders += self.folders[i][j] # Count all words in all folders
        if words_all_folders < requested_word_amount: # If the amount of words in all folders less than the requested amount
                                                      # ->
                                                      # print 'not enough'
            print u'Not enough words in the requested period'
        else: # If everything's OK
            for i in self.folders: # Start walking through the folders
                used_keys = [] # Used random keys from folder
                words_in_folder = 0 # Counter for all words in the current folder
                current_wordcount = 0 # Counter for words copied
                for j in self.folders[i]:
                    words_in_folder += self.folders[i][j] # Count all words in the current folder
                if words_in_folder > self.average_per_folder:
                    chosen_keys = []
                    while current_wordcount < self.average_per_folder:
                        random_file = random.choice(self.folders[i].keys())
                        chosen_keys.append(random_file)
                        if self.folders[i][random_file] < 300:
                            while self.folders[i][random_file] < 300:
                                random_file = random.choice(self.folders[i].keys())
                        if random_file not in used_keys:
                            if not os.path.exists(os.path.join(new_path,
                                                               os.path.basename(os.path.dirname(os.path.dirname(i))),
                                                               os.path.basename(os.path.dirname(i)),
                                                               os.path.basename(i),
                                                               os.path.basename(os.path.dirname(random_file)))):
                                os.makedirs(os.path.join(new_path,
                                                         os.path.basename(os.path.dirname(os.path.dirname(i))),
                                                         os.path.basename(os.path.dirname(i)),
                                                         os.path.basename(i),
                                                         os.path.basename(os.path.dirname(random_file))))
                            shutil.copy2(random_file, os.path.join(new_path,
                                         os.path.basename(os.path.dirname
                                                          (os.path.dirname
                                                           (os.path.dirname(random_file)))),
                                         os.path.basename(os.path.dirname
                                                          (os.path.dirname(random_file))),
                                         os.path.basename(os.path.dirname(random_file)),
                                         os.path.basename(random_file)))
                            print u'Words in the file copied: ' + str(self.folders[i][random_file])
                            self.words_copied += self.folders[i][random_file]
                            used_keys.append(random_file)
                            current_wordcount += self.folders[i][random_file]
                        if len(chosen_keys) == len(self.folders[i]):
                            break
                else:
                    if current_wordcount <= self.average_per_folder:
                        for j in self.folders[i]:
                            if self.folders[i][j] >= 300:
                                if not os.path.exists(os.path.join(new_path,
                                                      os.path.basename(os.path.dirname(os.path.dirname(i))),
                                                      os.path.basename(os.path.dirname(i)),
                                                      os.path.basename(os.path.dirname(j)))):
                                    os.makedirs(os.path.join(new_path,
                                                os.path.basename(os.path.dirname(os.path.dirname(i))),
                                                os.path.basename(os.path.dirname(i)),
                                                os.path.basename(os.path.dirname(j))))
                                shutil.copy2(j, os.path.join(new_path,
                                                 os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(j)))),
                                                 os.path.basename(os.path.dirname(os.path.dirname(j))),
                                                 os.path.basename(os.path.dirname(j)), os.path.basename(j)))
                                print u'Words in the file copied: ' + str(self.folders[i][j])
                                self.words_copied += self.folders[i][j]
                                current_wordcount += self.folders[i][j]
            print u'Total amount from ' + self.domain + ': ' + str(self.words_copied)
            if self.words_copied > actual_word_amount:
                            i = random.choice(self.folders.keys())
                            while self.words_copied > actual_word_amount:
                                 random_file = random.choice(self.folders[i].keys())
                                 random_file_to_delete = os.path.join(new_path,
                                             os.path.basename(os.path.dirname
                                                              (os.path.dirname
                                                               (os.path.dirname(random_file)))),
                                             os.path.basename(os.path.dirname
                                                              (os.path.dirname(random_file))),
                                             os.path.basename(os.path.dirname(random_file)),
                                             os.path.basename(random_file))
                                 if os.path.exists(random_file_to_delete):
                                     os.remove(random_file_to_delete)
                                     print u'Deleted file: ' + random_file_to_delete + u' ' + str(self.folders[i][random_file]) + u' words'
                                     self.words_copied -= self.folders[i][random_file]
                                 else:
                                     i = random.choice(self.folders.keys())

            print u'Total amount from ' + self.domain + ': ' + str(self.words_copied)


def main():
    copies = []
    all_words_copied = 0
    domains = sys.argv[6:]
    for k in range(len(domains)):
        copies.append(Newspaper())
    for i in range(len(copies)):
        print 'Domain: ' + domains[i]
        copies[i].domain = domains[i]
        copies[i].eval_period(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), domains[i])
        copies[i].count_dirs(domains[i])
        word_amount = (int(sys.argv[1])/len(domains)) + int(sys.argv[1])/(len(domains)*2)
        actual_word_amount = int(sys.argv[1])/len(domains)
        copies[i].count_average(word_amount)
        copies[i].find_wordcount(domains[i])
        copies[i].copy_files(domains[i], word_amount, actual_word_amount)
        all_words_copied += copies[i].words_copied
    print 'Total amount: ' + str(all_words_copied)
    if "-convert" in sys.argv:
        handler = newspapers.Handler()
        newspapers.convert_directory(sys.argv[1], sys.argv[2], handler)
        handler.saveTable(sys.argv[3], sys.argv[2])

if __name__ == "__main__":
    main()