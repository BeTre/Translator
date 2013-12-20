# -*- coding: utf-8 -*
#bootstrap
from flask import Flask, request, render_template, g
import csv
import sqlite3

app = Flask(__name__)

csv_delimiter = ','
csv_quotechar = "\""
input_file = 'vocabulary_list.csv'
output_file = 'vocabulary_list.csv'
database = 'vocabulary.db'
database_csv = ['csv/verb.csv', 'csv/noun.csv', 'csv/adjective.csv', 'csv/numbers.csv', 'csv/countries.csv', 'csv/no_type.csv']
#Abbreviations: language to translate: ltt, language to learn: ltl


###CSV-functions###############################################################
def readin_csv(input_file):
    '''Read in utf-8 csv file and return unicode list.'''
    with open(input_file, 'r') as csvfile:
        readin = csv.reader(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
        voclist = []
        for line in readin:
            line_decoded = []
            for element in line:
                line_decoded.append(element.decode('utf-8'))
            voclist.append(line_decoded)
        return voclist


def readout_csv(voclist, output_file):
    '''Read out unicode list 'voclist' in utf-8 csv file.'''
    with open(output_file, 'w') as csvfile:
        readout = csv.writer(csvfile, delimiter=csv_delimiter, quotechar=csv_quotechar)
        for line in voclist:
            line_encoded = []
            for element in line:
                line_encoded.append(element.encode('utf-8'))
            readout.writerow(line_encoded)


###DB-functions################################################################
@app.before_request
def before_request():
    g.db = sqlite3.connect(database)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def fetch_word_cases(word_type_id):
    '''Read out all word cases to specifiv word type.'''
    cur = g.db.execute('''
    select
        wc.case_order, wc.name, wc.id
    from
        word_cases as wc
        join word_types as wt on wc.word_type_id = wt.id
    where
        wt.id = ?
    order by wc.case_order''', (word_type_id,))
    data = [[row[1], row[2]] for row in cur]
    return data


def fetch_word_types():
    '''Read out all word types.'''
    cur = g.db.execute('select wt.id, wt.name from word_types as wt')
    data = {row[0]: row[1] for row in cur}
    return data


def fetch_languages():
    '''Read out all languages.'''
    cur = g.db.execute('select name from languages')
    data = [row[0] for row in cur]
    return data


def fetch_lectures():
    '''Read out all languages.'''
    cur = g.db.execute('select name from lectures')
    data = [row[0] for row in cur]
    return data


def add_group_to_db(ltt, ltl, lecture, word_to_translate, translations):
    '''needed keys: variable ltt: str(language to translate), e.g. 'German', needs to be in db
                    variable ltl: str(language to learn), e.g. 'Swedish', needs to be in db
                    variable lecture: str(lecture), e.g. 'Book 1, Lecture 5', needs to be in db
                    dictionary word_to_translate'{name, case, learned (optional), irregular (optional)}
                        e.g. word_to_translate{name: 'laufen', case: '1', learned: '1', irregular: '0'}
                    dictionaries of cases of translations
                        e.g. translations{case_1: {name: 'go', case: '1', learned: '1', irregular: '0'},
                                          case_2: {name: 'went', case: '2', learned: '1', irregular: '1'},
                                          case_3: {name: 'gone', case: '3', learned: '0', irregular: '1'}'''
    #get language_ids and translation order
    cur = g.db.execute('''select id, translation_order from languages where name = ?''', (ltt,))
    ltt_id, translation_order_ltt = cur.fetchone()
    cur = g.db.execute('''select id, translation_order from languages where name = ?''', (ltl,))
    ltl_id, translation_order_ltl = cur.fetchone()

    #get lecture_id
    cur = g.db.execute('''select id from lectures where name = ?''', (lecture, ))
    (lecture_id, ) = cur.fetchone()

    #insert new groups
    cur = g.db.execute('''select max(id) from groups''')
    next_group_id_ltt = cur.fetchone()[0]+1
    next_group_id_ltl = next_group_id_ltt+1
    cur = g.db.executemany('''INSERT into groups (id) values (?)''', [(next_group_id_ltt,), (next_group_id_ltl,)])

    #insert translation realtion between groups;
    if translation_order_ltt < translation_order_ltl:
        cur = g.db.execute('''INSERT into translations (group_lower_translation_order_id,
                           group_higher_language_order_id) values (?,?)''', (next_group_id_ltt, next_group_id_ltl))
    else:
        cur = g.db.execute('''INSERT into translations (group_lower_translation_order_id,
                           group_higher_language_order_id) values (?,?)''', (next_group_id_ltl, next_group_id_ltt))

    #insert word to translate
    cur = g.db.execute('''INSERT into words
                       (name, word_case_id, learned, irregular, group_id, language_id, lecture_id)
                       values (?,?,?,?,?,?,?)''',
                       (word_to_translate['name'], word_to_translate['case'],
                        word_to_translate.get('learned', 0), word_to_translate.get('irregular', 0),
                        next_group_id_ltt, ltt_id, lecture_id))

    #insert translations
    for key in translations:
        cur = g.db.execute('''INSERT into words
                           (name, word_case_id, learned, irregular, group_id, language_id, lecture_id)
                           values (?,?,?,?,?,?,?)''',
                           (translations[key]['name'], translations[key]['case'],
                            translations[key].get('learned', 0), translations[key].get('irregular', 0),
                            next_group_id_ltl, ltl_id, lecture_id))
    #g.db.commit()
    return 'word %s sucessfully added' % (word_to_translate['name'])


###CSV-sites###################################################################
@app.route('/')
def index():
    'list of vocabulary from csv file'
    voclist = readin_csv(input_file)
    return render_template('list.html', voclist=voclist)


@app.route('/learn/<int:learn_id>', methods=['GET'])
def learn(learn_id):
    'learning of vocabularies based on simple csv file'
    voclist = readin_csv(input_file)

    if 'vocabulary' in request.args:
        vocabulary = request.args['vocabulary']
        last_answer = vocabulary
        if vocabulary == voclist[learn_id][1]:
            voclist[learn_id][2] = '1'
            correct = True
            learn_id += 1
        else:
            voclist[learn_id][2] = '0'
            correct = voclist[learn_id][1]
        readout_csv(voclist, output_file)
    else:
        correct = 'start'
        last_answer = []

    if 'Mark as learned' in request.args:
        voclist[learn_id][2] = '1'
        learn_id += 1
        readout_csv(voclist, output_file)

    next_unlearned = learn_id+1
    while voclist[next_unlearned][2] == '1':
        next_unlearned += 1

    return render_template('learn.html', voc_to_translate=voclist[learn_id][0], learn_id=learn_id,
                           last_answer=last_answer, correct=correct, next_unlearned=next_unlearned)


###DB-sites####################################################################
@app.route('/start')
def start():
    '''choose languages to translate'''
    languages = fetch_languages()
    lectures = fetch_lectures()
    return render_template('start.html', languages=languages, lectures=lectures)


@app.route('/add', methods=['GET', 'POST'])
def add():
    data = request.form
    ltt = data['ltt']
    ltl = data['ltl']
    lecture = data['lecture']
    word_types = fetch_word_types()
    return render_template('add.html', word_types=word_types,
                           ltt=ltt, ltl=ltl, lecture=lecture)


@app.route('/add/<word_type_id>', methods=['GET', 'POST'])
def add_word(word_type_id):
    data = request.form
    print data
    word_cases_ordered = fetch_word_cases(word_type_id)
    return render_template('add_voc.html', word_type_id=word_type_id, word_cases_ordered=word_cases_ordered,
                           ltt=data['ltt'], ltl=data['ltl'], lecture=data['lecture'])


@app.route('/add/new', methods=['GET', 'POST'])
def add_word_to_db():
    data = request.form
    print data
    ltt = data['ltt']
    ltl = data['ltl']
    lecture = data['lecture']
    word_to_translate = {'name': data['word_to_translate'],
                         'case': data['case_word_to_translate'],
                         'learned': data.get('learned_word_to_translate', 0),
                         'irregular': data.get('ir_word_to_translate', 0)}
    for key in data:
        if key[:4] == 'case' and key != 'case_word_to_translate':
            print 'key in if:', key
            translations = {key: {'name': data[key],
                                  'case': key[5:],
                                  'learned': data.get('learned_'+key, 0),
                                  'irregular': data.get('ir_'+key, 0)}}
            print 'added', key, data[key]
    print word_to_translate, translations
    return add_group_to_db(ltt, ltl, lecture, word_to_translate, translations)


#Readin_csv_to_db_part
@app.route('/import')
def imports():
    'list of vocabulary from csv file'
    voclist = readin_csv(database_csv[0])
    return render_template('list.html', voclist=voclist)

if __name__ == '__main__':
    app.run(debug=True)
