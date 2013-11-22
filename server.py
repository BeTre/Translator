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
        reader = csv.reader(csvfile)
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
	readin = csv.reader(open('vocabulary_list.csv', 'r'))
	voclist = list(readin)


	f = open('learn.html', 'w')
	f.write('''<!DOCTYPE html>
	<html>
	<body>
	<h3>Vokabeltraining</h3>\n''')
	f.write(voclist[learn_id][0]+'\n')
	f.write('''<form name='input'
	action='/learn/'''+str(learn_id)+''''
	method='get'>Übersetzung:<input type='text' name='vocabulary'>
	<input type='submit' value='Submit'>
	</form>''')
	f.write('\n')
	f.write('''<a href='/learn/%i'>nächste Vokabel</a>'''%(learn_id+1))
	vocabulary = request.args.get('vocabulary')
	if unicode(vocabulary).encode('utf-8') == voclist[learn_id][1]:
		f.write('RICHTIG')
		voclist[learn_id][2] = 1
	else:
		f.write('FALSCH\n')
		f.write(unicode(vocabulary).encode('utf-8')+'\n')
		voclist[learn_id][2] = 0
	f.close()


	with open('vocabulary_list2.csv', 'w') as csvfile:
		readout = csv.writer(csvfile)
		for line in voclist:
			readout.writerow(line)

	f = open('learn.html', 'r')
	return f.read()



if __name__ == '__main__':
    app.run(debug=True)
