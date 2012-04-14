#!/usr/bin/env python

import csv
csv_reader=csv.reader(open('train.csv', 'rb'), delimiter=',')

f = open('train.txt', 'w')
fixed_width = 20

for row in csv_reader:
    s = ''
    for index, value in enumerate(row):
        value_str =  str(float(value) / 20000.) + ' ' if index == 0 else str(index) + ':' + str(value) + ' '
        if len(value_str) < fixed_width:
            value_str += ' ' * (fixed_width - len(value_str))
        s += value_str
    s += '\n'
    f.write(s)
f.close()
        
        
        
        




