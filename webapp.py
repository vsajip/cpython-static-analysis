#!/usr/bin/env python
#
# Copyright (C) 2019 Vinay Sajip. MIT Licenced.
#
import argparse
import configparser
import logging
import os
import sqlite3
import time
import types

import bottle
import jwt


logger = logging.getLogger(__name__)


class App(bottle.Bottle):
    pass


app = App()


def index():
    tpl = bottle.SimpleTemplate(name='index.tpl',
                                lookup=bottle.TEMPLATE_PATH)
    conn = sqlite3.connect('statics.sqlite')
    cur = conn.cursor()
    cur.execute('select id, name, storage_class, type_text, filename, '
                'start_line, start_column, end_line, end_column from statics '
                'order by filename, start_line')
    dbrows = cur.fetchall()
    rows = []
    for row in dbrows:
        o = types.SimpleNamespace(id=row[0], name=row[1], storage_class=row[2],
                            type_text=row[3], filename=row[4], start_line=row[5],
                            start_column=row[6], end_line=row[7],
                            end_column=row[8])
        rows.append(o)
    cur.close()
    conn.close()
    context = {'rows': rows}
    result = tpl.render(**context)
    return result


def update(name, storage_class, type_text, filename, start_line, start_column,
           end_line, end_column):
    SEL_SQL = ('select id, name, storage_class, type_text, filename, '
               'start_line, start_column, end_line, end_column from statics '
               'where filename = ? and name = ?')
    INS_SQL = ('insert into statics (name, storage_class, type_text, filename, '
               'start_line, start_column, end_line, end_column, mark) '
               'values (?, ?, ?, ?, ?, ?, ?, ?, ?)'
              )
    UPD_SQL = ('update statics set name = ?, storage_class = ?, type_text = ?, '
               'filename = ?, start_line = ?, start_column = ?, end_line = ?, '
               'end_column = ?, mark = ? where id = ?'
              )
    conn = sqlite3.connect('statics.sqlite')
    cur = conn.cursor()
    cur.execute(SEL_SQL, (filename, name))
    rows = cur.fetchall()
    updated = False
    if not rows:
        cur.execute(INS_SQL, (name, storage_class, type_text, filename,
                              start_line, start_column, end_line, end_column,
                              None))
        updated = True
    elif len(rows) > 1:
        logger.error('multiple rows unexpected: %s', rows)
        bottle.abort(500)
    else:
        row = rows[0]
        changed = []
        if name != row[1]:
            changed.append('name: %s -> %s' % (row[1], name))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if storage_class != row[2]:
            changed.append('storage_class: %s -> %s' % (row[2], storage_class))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if type_text != row[3]:
            changed.append('type_text: %s -> %s' % (row[3], type_text))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if filename != row[4]:
            changed.append('filename: %s -> %s' % (row[4], filename))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if start_line != row[5]:
            changed.append('start_line: %s -> %s' % (row[5], start_line))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if start_column != row[6]:
            changed.append('start_column: %s -> %s' % (row[6], start_column))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if end_line != row[7]:
            changed.append('end_line: %s -> %s' % (row[7], end_line))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if end_column != row[8]:
            changed.append('end_column: %s -> %s' % (row[8], end_column))
            logger.debug('changed: %s: %s', (filename, name), changed[-1])
        if changed:
            rid = row[0]
            cur.execute(UPD_SQL, (name, storage_class, type_text, filename,
                                  start_line, start_column, end_line, end_column,
                                  None, rid))
            updated = True
    cur.close()
    if updated:
        conn.commit()
    return 200 if updated else 202


def statics_analysis():
    r = bottle.request
    if r.method == 'GET':
        return index()

    # handle POST request
    auth = r.headers.get('Authorization')
    if not auth or not auth.startswith('Bearer '):
        bottle.abort(403)
    auth = auth[7:].encode('utf-8')
    payload = jwt.decode(auth, app.secret, algorithms='HS256')
    tnow = time.time()
    # if 'nbf' not in payload or tnow < payload['nbf']:
        # bottle.abort(400)
    if 'exp' not in payload or tnow > payload['exp']:
        bottle.abort(400)
    rc = update(payload['name'], payload['storage_class'], payload['type_text'],
                payload['filename'], payload['start_line'], payload['start_column'],
                payload['end_line'], payload['end_column'])
    bottle.response.status = rc
    return 'Updated OK'


def favicon():
    bottle.redirect('https://red-dove.com/favicon.ico')


def setup():
    if not os.path.isfile('config.ini'):
        app.secret = None
    else:
        cp = configparser.ConfigParser()
        cp.read('config.ini')
        app.secret = cp['DEFAULT']['secret']

    app.route('/', ['GET'], index)
    app.route('/favicon.ico', ['GET'], favicon)
    app.route('/statics-analysis/', ['GET', 'POST'], statics_analysis)


setup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    app.run(host='127.0.0.1', port=5001, debug=True, reloader=True)

