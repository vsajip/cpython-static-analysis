#
# Copyright (C) 2019 Red Dove Consultants Limited
#

import datetime
import sqlite3
from types import SimpleNamespace

import bottle

class App(bottle.Bottle):
    pass

app = App()

def index():
    tpl = bottle.SimpleTemplate(name='index.tpl',
                                lookup=bottle.TEMPLATE_PATH)
    context = {'app': app}
    result = tpl.render(**context)
    return result

def favicon():
    bottle.redirect('https://red-dove.com/favicon.ico')

def setup():
    app.route('/', ['GET'], index)
    app.route('/favicon.ico', ['GET'], favicon)
    conn = sqlite3.connect('statics.sqlite')
    cur = conn.cursor()
    cur.execute('select id, name, storage_class, type_text, filename, '
                'start_line, start_column, end_line, end_column from statics '
                'order by filename, start_line')
    dbrows = cur.fetchall()
    app.rows = rows = []
    for row in dbrows:
        o = SimpleNamespace(id=row[0], name=row[1], storage_class=row[2],
                            type_text=row[3], filename=row[4], start_line=row[5],
                            start_column=row[6], end_line=row[7],
                            end_column=row[8])
        rows.append(o)
    cur.close()
    conn.close()

setup()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True, reloader=True)
