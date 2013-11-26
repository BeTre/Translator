# -*- coding: utf-8 -*
#python
#flask
#html

#http

#bootstrap
#SQL
#sqlite

from flask import Flask
from flask import request
from numpy import loadtxt
import csv

app = Flask(__name__)

csv_delimiter = ','
csv_quotechar = "'"


@app.route('/')
def index():
    f = open('index.html', 'w')
    f.write('''<!DOCTYPE html>
    <html>
    <body>
    <h3>Vokabelliste</h3>
    <table border='1'>
    <tr>
    <th>Deutsch</th>
    <th>Schwedisch</th>
    </tr>\n''')

    with open('vocabulary_list.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
        for row in reader:
            f.write('<tr>\n')
            for element in row:
                f.write('<td>')
                f.write(element)
                f.write('</td>\n')
            f.write('</tr>\n')
    f.write('''
    </table>
    </body>
    </html>''')
    f.close()
    f = open('index.html', 'r')
    return f.read()

@app.route('/new')
def new():
    a = 'hallo'
    return a

@app.route('/learn/<int:learn_id>', methods=['GET'])
def show_learn(learn_id):
    readin = csv.reader(open('vocabulary_list.csv', 'r'), delimiter=csv_delimiter, quotechar=csv_quotechar)
    voclist = list(readin)

    site = '''<!DOCTYPE html>
    <html>
    <body>
    <h3>Vokabeltraining</h3>\n'''+voclist[learn_id][0]+'\n'+'''<form name='input'
    action='/learn/'''+str(learn_id)+''''
    method='get'>Übersetzung:<input type='text' name='vocabulary'>
    <input type='submit' value='Submit'>
    </form>'''+'\n'+'\n'+'''<a href='/learn/{nextpage}'>nächste Vokabel</a>'''.format(nextpage=learn_id+1)
    if 'vocabulary' in request.args:
        vocabulary = request.args['vocabulary']
        if unicode(vocabulary).encode('utf-8') == voclist[learn_id][1]:
            site += 'RICHTIG'
            voclist[learn_id][2] = 1
        else:
            site += 'FALSCH'+'\n'+unicode(vocabulary).encode('utf-8')+'\n'
            voclist[learn_id][2] = 0

    with open('vocabulary_list.csv', 'w') as csvfile:
        readout = csv.writer(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
        for line in voclist:
            readout.writerow(line)
    return site


if __name__ == '__main__':
    app.run(debug=True)
