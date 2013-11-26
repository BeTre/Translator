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
from flask import render_template
import csv

app = Flask(__name__)

csv_delimiter = ','
csv_quotechar = "\""
input_file = 'vocabulary_list.csv'
output_file = 'vocabulary_list2.csv'

def readin_csv(input_file):
    '''read in utf-8 csv file and return unicode list'''
    with open(input_file, 'r') as csvfile:
        readin = csv.reader(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
        voclist = []
        for line in readin:
            line_decoded = []
            for element in line:
                line_decoded.append(element.decode('utf-8'))
            voclist.append(line_decoded)
        return voclist


@app.route('/')
def index():
    voclist = readin_csv(input_file)
    return render_template('list.html', voclist = voclist)


@app.route('/learn/<int:learn_id>', methods=['GET'])
def learn(learn_id):
    voclist = readin_csv(input_file)

    if 'vocabulary' in request.args:
        vocabulary = request.args['vocabulary']
        if vocabulary == voclist[learn_id][1]:
            voclist[learn_id][2] = '1'
            correct = True
        else:
            voclist[learn_id][2] = '0'
            correct = voclist[learn_id][1]
        with open(output_file, 'w') as csvfile:
            readout = csv.writer(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
            for line in voclist:
                line2 = []
                for element in line:
                    line2.append(element.encode('utf-8'))
                readout.writerow(line2)
    else:
        correct = 'start'


    return render_template('learn.html', voc_to_translate = voclist[learn_id][0], learn_id = learn_id, correct = correct)


if __name__ == '__main__':
    app.run(debug=True)
