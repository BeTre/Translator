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
import csv

app = Flask(__name__)

@app.route("/")
def index():
    f = open("index.html", "w")
    f.write("""<!DOCTYPE html>
    <html>
    <body>
    <h3>Vokabelliste</h3>
    <table border="1">
    <tr>
    <th>Deutsch</th>
    <th>Schwedisch</th>
    </tr>\n""")
    with open('vokabelliste.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            f.write("<tr>\n")
            for element in row:
                f.write("<td>")
                f.write(element)
                f.write("</td>\n")
            f.write("</tr>\n")
    f.write("""
    </table>
    </body>
    </html>""")
    f.close()
    f = open("index.html", "r")
    return f.read()


@app.route('/post/<int:post_id>')
def show_post(post_id):
    # show the post with the given id, the id is an integer
    return 'Post %d' % post_id

@app.route("/learn/<int:learn_id>", methods=["GET"])
def show_learn(learn_id):
    with open('vokabelliste.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        k = 0
        for row in reader:
            k += 1
            if k == learn_id:
                f = open("learn.html", "w")
                f.write("""<!DOCTYPE html>
                <html>
                <body>
                <h3>Vokabeltraining</h3>\n""")
                f.write(row[0]+"\n")
                f.write("""<form name="input"
                action="/learn/"""+str(learn_id)+""""
                method="get">Übersetzung:<input type="text" name="vocabulary">
                <input type="submit" value="Submit">
                </form>""")
                f.write("\n")
                f.write("""<a href="/learn/%i">nächste Vokabel</a>"""%(learn_id+1))
                vocabulary = request.args.get("vocabulary")
                if unicode(vocabulary).encode("utf-8") == row[1]:
                    f.write("RICHTIG")
                else:
                    f.write("FALSCH\n")
                    f.write(unicode(vocabulary).encode("utf-8")+"\n")
                f.close()
        f = open("learn.html", "r")
        return f.read()


if __name__ == "__main__":
    app.run(debug=True)
