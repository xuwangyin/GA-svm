#!/usr/bin/env python

import csv
csv_reader=csv.reader(open('test.csv', 'rb'), delimiter=',')

f = open('test.txt', 'w')

for row in csv_reader:
    s = ''
    for index, value in enumerate(row):
        s = s + str(value) + ' ' if index == 0 else s + str(index) + ':' + str(value) + ' '
    s += '\n'
    f.write(s)
f.close()
        
        
        
        




