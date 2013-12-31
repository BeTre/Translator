# -*- coding: utf-8 -*
import csv

import sqlite3
from flask import Flask, request, render_template, g, jsonify

app = Flask(__name__)

csv_delimiter = ','
csv_quotechar = '"'
input_file_name = 'vocabulary_list.csv'
output_file_name = 'vocabulary_list.csv'
database = 'vocabulary.db'
database_csv = [
    'csv/verb.csv', 'csv/noun.csv', 'csv/adjective.csv',
    'csv/numbers.csv', 'csv/countries.csv', 'csv/no_type.csv'
    ]


# CSV-functions#########################################################
def read_csv(input_file_name):
    """Read utf-8 csv file and return list of unicode strings"""
    with open(input_file_name) as csvfile:
        readin = csv.reader(csvfile, delimiter=csv_delimiter,
                            quotechar=csv_quotechar)
        voclist = []
        for line in readin:
            line_decoded = []
            for element in line:
                line_decoded.append(element.decode('utf-8'))
            voclist.append(line_decoded)
        return voclist


def write_csv(voclist, output_file_name):
    """Write unicode list 'voclist' in utf-8 csv file."""
    with open(output_file_name, 'w') as csvfile:
        readout = csv.writer(csvfile, delimiter=csv_delimiter,
                             quotechar=csv_quotechar)
        for line in voclist:
            line_encoded = []
            for element in line:
                line_encoded.append(element.encode('utf-8'))
            readout.writerow(line_encoded)


# DB-functions##########################################################
@app.before_request
def before_request():
    g.db = sqlite3.connect(database)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def fetch_word_cases_of_language(word_type_id, language_id):
    """Read out all word cases to specifiv word type and language."""
    cur = g.db.execute('''
    select
        wc.name, wc.id
    from
        word_cases as wc
        join word_types as wt on wc.word_type_id = wt.id
    where
        wt.id = :word_type_id
    and
        wc.language_id = :language_id
    order by wc.case_order''',
    {'word_type_id' : word_type_id, 'language_id': language_id})
    data = [[row[0], row[1]] for row in cur]
    return data


def fetch_word_types():
    """Read out all word types."""
    cur = g.db.execute('select wt.id, wt.name from word_types as wt')
    data = {row[0]: row[1] for row in cur}
    return data


def fetch_languages():
    """Read out all languages."""
    cur = g.db.execute('select name from languages')
    data = [row[0] for row in cur]
    return data


def fetch_lectures():
    """Read out all languages."""
    cur = g.db.execute('select name from lectures')
    data = [row[0] for row in cur]
    return data


def insert_word(
        group_id, language_id, lecture_id, name,
        case_id, learned=False, irregular=False):
    g.db.execute('''
                 INSERT into words (
                     name, word_case_id, learned, irregular,
                     group_id, language_id, lecture_id
                     )
                 values (?,?,?,?,?,?,?)''',
                 (name, case_id, learned, irregular,
                  group_id, language_id, lecture_id))
                 # False = 0 in db?


def insert_groups():
    cur = g.db.execute('select max(id) from groups')
    lower_group_id = cur.fetchone()[0]+1
    higher_group_id = lower_group_id+1
    cur = g.db.executemany('INSERT into groups (id) values (?)',
                           [(lower_group_id,), (higher_group_id,)])
    cur = g.db.execute('''
                       INSERT into translations
                       (group_lower_translation_order_id,
                        group_higher_translation_order_id)
                       values (?,?)''',
                       (lower_group_id, higher_group_id))
    return lower_group_id, higher_group_id


def add_group_to_db(
        lang_from, lang_to, lecture, word_to_translate, translations):
    '''needed keys: variable lang_from: str(language to translate), e.g. 'German', needs to be in db
                    variable lang_to: str(language to learn), e.g. 'Swedish', needs to be in db
                    variable lecture: str(lecture), e.g. 'Book 1, Lecture 5', needs to be in db
                    dictionary word_to_translate'{name, case, learned (optional), irregular (optional)}
                        e.g. word_to_translate{name: 'laufen', case: '1', learned: '1', irregular: '0'}
                    dictionaries of cases of translations
                        e.g. translations[{name: 'go', case: '1', learned: '1', irregular: '0'},
                                          {name: 'went', case: '2', learned: '1', irregular: '1'},
                                          {name: 'gone', case: '3', learned: '0', irregular: '1'}]'''

    lower_group_id, higher_group_id = insert_groups()

    ((lang_from_id, translation_order_lang_from),) = g.db.execute('''
    select id, translation_order from languages where name = ?''', (lang_from, ))
    ((lang_to_id, translation_order_lang_to),) = g.db.execute('''
    select id, translation_order from languages where name = ?''', (lang_to, ))
    ((lecture_id,),) = g.db.execute('''
    select id from lectures where name = ?''', (lecture, ))

    if translation_order_lang_from < translation_order_lang_to:
        group_id_lang_from, group_id_lang_to = lower_group_id, higher_group_id
    else:
        group_id_lang_from, group_id_lang_to = higher_group_id, lower_group_id

    # insert word to translate
    insert_word(group_id_lang_from, lang_from_id, lecture_id,
                word_to_translate['name'], word_to_translate['case'],
                word_to_translate.get('learned', False),
                word_to_translate.get('irregular', False))

    # insert translations
    for trans in translations:
        insert_word(group_id_lang_to, lang_to_id, lecture_id,
                    trans['name'], trans['case'],
                    trans.get('learned', False),
                    trans.get('irregular', False))
    g.db.commit()
    return 'word %s sucessfully added' % (word_to_translate['name'])


def fetch_word_case_count():
    """
    Returns the number of words for each word case
    dict(key=word_case_name, value=number_of_words)

    """
    cur = g.db.execute('''
        select
           wc.name, count(wc.id)
        from
            words w
            join word_cases wc on w.word_case_id = wc.id
        group by
            wc.id''')
    return {row[0]: row[1] for row in cur}


# CSV-sites#############################################################
@app.route('/list')
def list():
    'list of vocabulary from csv file'
    voclist = read_csv(input_file_name)
    return render_template('list.html', voclist=voclist)


@app.route('/learn/<int:learn_id>', methods=['GET'])
def learn(learn_id):
    'learning of vocabularies based on simple csv file'
    voclist = read_csv(input_file_name)

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
        write_csv(voclist, output_file_name)
    else:
        correct = 'start'
        last_answer = []

    if 'Mark as learned' in request.args:
        voclist[learn_id][2] = '1'
        learn_id += 1
        write_csv(voclist, output_file_name)

    next_unlearned = learn_id+1
    while voclist[next_unlearned][2] == '1':
        next_unlearned += 1

    return render_template('learn.html',
                           voc_to_translate=voclist[learn_id][0],
                           learn_id=learn_id,
                           last_answer=last_answer, correct=correct,
                           next_unlearned=next_unlearned)


###DB-sites#############################################################
@app.route('/start')
def start():
    """choose languages to translate"""
    languages = fetch_languages()
    lectures = fetch_lectures()
    return render_template('start.html',
                           languages=languages, lectures=lectures)


@app.route('/add', methods=['GET', 'POST'])
def add():
    data = request.form
    lang_from = data['lang_from']
    lang_to = data['lang_to']
    lecture = data['lecture']
    word_types = fetch_word_types()
    return render_template('add.html', word_types=word_types,
                           lang_from=lang_from, lang_to=lang_to,
                           lecture=lecture)


@app.route('/add/<word_type_id>', methods=['GET', 'POST'])
def add_word(word_type_id):
    data = request.form

    ((lang_from_id,),) = g.db.execute('''
    select id from languages where name = ?''', (data['lang_from'], ))
    ((lang_to_id,),) = g.db.execute('''
    select id from languages where name = ?''', (data['lang_to'], ))

    word_cases_lang_from = fetch_word_cases_of_language(word_type_id,
                                                        lang_from_id)
    word_cases_lang_to = fetch_word_cases_of_language(word_type_id,
                                                      lang_to_id)
    print word_cases_lang_from
    print word_cases_lang_to
    return render_template('add_voc.html', word_type_id=word_type_id,
                           word_cases_lang_from=word_cases_lang_from,
                           word_cases_lang_to=word_cases_lang_to,
                           lang_from=data['lang_from'],
                           lang_to=data['lang_to'], lecture=data['lecture'])


@app.route('/add/new', methods=['GET', 'POST'])
def add_word_to_db():
    data = request.form
    print data
    lang_from = data['lang_from']
    lang_to = data['lang_to']
    lecture = data['lecture']
    word_to_translate = {'name': data['word_to_translate'],
                         'case': data['case_word_to_translate'],
                         'learned': data.get('learned_word_to_translate', 0),
                         'irregular': data.get('ir_word_to_translate', 0)}
    translations = []
    for key in data:
        if key.startswith('case') and key != 'case_word_to_translate':
            translations.append({'name': data[key],
                                 'case': key[5:],
                                 'learned': data.get('learned_'+key, 0),
                                 'irregular': data.get('ir_'+key, 0)})

    return add_group_to_db(lang_from, lang_to, lecture,
                           word_to_translate, translations)


# read_csv_to_db_part
@app.route('/import')
def imports():
    """list of vocabulary from csv file"""
    voclist = read_csv(database_csv[0])
    return render_template('list.html', voclist=voclist)


@app.route('/word_case_chart_data')
def word_case_chart_data():
    word_case_count = fetch_word_case_count()
    l = []
    for case in sorted(word_case_count):
        l.append([case, word_case_count[case]])
    return jsonify({'chart_data': l})


@app.route('/word_case_chart')
def word_case_chart():
    return render_template('word_case_chart.html')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
