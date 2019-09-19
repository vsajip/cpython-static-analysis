#!/usr/bin/env python
#
# Copyright (C) 2019 Vinay Sajip. MIT Licenced.
#
import argparse
import json
import logging
import os
import re


logger = logging.getLogger(__name__)


CONST_STRUCT_TYPES = re.compile('const (struct|union) '
                                '(_frozen|dbcs_map|normal_encoding|arraydescr|'
                                'iso2022_config)')

IGNORED_STRUCT_TYPES = re.compile('(struct )?Py(Module|Method)Def')

CONST_TYPES = re.compile(r'const ((unsigned )?(char|int|short|long)|'
                         'MultibyteCodec|IntConstantPair|arc|DBCHAR|'
                         'XML_Char|XML_Feature|size_t|time_t|double|mpd_t|'
                         'mpd_size_t|mpd_uint_t|encodefuncentry|dfa|label|'
                         'int16_t|int32_t|uint16_t|uint32_t)'
                         r'( (\*const )?\[\d+\])?')


PYTHON_DIR = os.path.expanduser('~/projects/python/master')


def get_diag_info(diag):
    result = {}
    for k in ('spelling', 'location', 'severity', 'ranges', 'fixits'):
        result[k] = getattr(diag, k)
    return result


def run_query(conn, sql, args, update=False):
    cur = conn.cursor()
    cur.execute(sql, args)
    result = cur.fetchall()
    if update:
        conn.commit()
    cur.close()
    return result


def register_static(options, name, storage_class, type_text, filename,
                    start_line, start_column, end_line, end_column):
    SEL_SQL = 'select id from statics where filename = ? and name = ?'
    INS_SQL = ('insert into statics (name, storage_class, type_text, filename, '
               'start_line, start_column, end_line, end_column, mark) '
               'values (?, ?, ?, ?, ?, ?, ?, ?, ?)'
              )
    UPD_SQL = ('update statics set name = ?, storage_class = ?, type_text = ?, '
               'filename = ?, start_line = ?, start_column = ?, end_line = ?, '
               'end_column = ?, mark = ? where id = ?'
              )
    cur = options.conn.cursor()
    cur.execute(SEL_SQL, (filename, name))
    rows = cur.fetchall()
    if not rows:
        cur.execute(INS_SQL, (name, storage_class, type_text, filename,
                              start_line, start_column, end_line, end_column,
                              None))
    else:
        assert(len(rows) == 1)
        rid = rows[0][0]
        cur.execute(UPD_SQL, (name, storage_class, type_text, filename,
                              start_line, start_column, end_line, end_column,
                              None, rid))
    options.conn.commit()
    cur.close()


def walk_ast(node):
    yield node
    for child in node.get_children():
        yield from walk_ast(child)


def find_c_file(parts):
    for p in parts:
        if p.endswith('.c'):
            return p


def compute_header_paths():
    import re
    import subprocess

    START_LINE = re.compile(br'^#include\s.*search starts here:')
    END_LINE = re.compile(b'^End of search list.')
    INCLUDE_LINE = re.compile(br'^\s+([^\(]+)\s*')

    result = []
    p = subprocess.Popen('cpp -v /dev/null'.split(),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    _, stderr = p.communicate()
    in_includes = False
    flag = b'-I'
    for line in stderr.splitlines():
        if END_LINE.search(line):
            in_includes = False
        if in_includes:
            m = INCLUDE_LINE.search(line)
            if m:
                result.append(flag + line.strip())
        if START_LINE.search(line):
            in_includes = True
    return [s.decode('utf-8') for s in result]


def compute_args_linux(options):
    result = {}
    header_paths = compute_header_paths()
    python_dir = options.python_dir
    with open(options.compute_args, encoding='utf-8') as f:
        for line in f:
            if not line.startswith('gcc ') or ' -shared' in line:
                continue
            parts = line.split()
            fn = find_c_file(parts)
            if not fn:
                continue
            p = os.path.abspath(os.path.join(python_dir, fn))
            if os.path.isfile(p):
                rp = os.path.relpath(p, python_dir)
                args = []
                for item in parts:
                    if item.startswith('-I'):
                        s = item[2:]
                        s = os.path.abspath(os.path.join(python_dir, s))
                        args.append('-I%s' % s)
                    elif item.startswith('-D'):
                        args.append(item)
                args.extend(header_paths)
                args.append(p)
                result[rp] = args
    print(json.dumps(result, sort_keys=True, indent=2))


def compute_args_windows(options):
    result = {}
    with open(options.compute_args, encoding='utf-8') as f:
        python_dir = options.python_dir
        build_dir = os.path.join(python_dir, 'PCbuild')
        for line in f:
            s = line.lower()
            if 'tracker.exe' in s:
                continue
            if 'cl.exe' not in s:
                continue
            opts = []
            cfiles = []
            parts = line.split()
            for i, p in enumerate(parts):
                if p.startswith('/I'):
                    opts.append('-I%s' % p[2:])
                elif p == '/D':
                    opts.append('-D%s' % parts[i + 1])
                elif p.endswith('.c'):
                    if not os.path.isabs(p):
                        cp = os.path.abspath(os.path.join(build_dir, p))
                        cfiles.append(cp)
            for p in cfiles:
                rp = os.path.relpath(p, python_dir).replace(os.sep, '/')
                args = opts + [p]
                result[rp] = args
    print(json.dumps(result, sort_keys=True, indent=2))


def compute_statics(options):
    import shutil
    import sqlite3

    from clang.cindex import Index, Config, CursorKind, StorageClass

    SCTEXT = {
        StorageClass.STATIC: 'static',
        StorageClass.NONE: 'implicit',
        StorageClass.EXTERN: 'extern',
    }

    Config.set_library_path(options.clang_dir)
    index = Index.create()

    if not os.path.isfile(options.args):
        raise ValueError('No arguments file: %s.' % options.args)

    with open(options.args, encoding='utf-8')  as f:
        arglists = json.load(f)

    if options.new or not os.path.isfile(options.database):
        logger.info('Creating new database from template: %s.', options.database)
        shutil.copyfile('statics.template.sqlite', options.database)

    options.conn = sqlite3.connect(options.database)
    logger.info('Computing statics into %s.', options.database)

    for rp in sorted(arglists):
        p = os.path.join(options.python_dir, rp)
        args = arglists[rp]
        tu = index.parse(None, args)
        if not tu:
            logger.warning('Unable to parse %s.', rp)
            continue
        diags = list(tu.diagnostics)
        if not diags:
            s = ''
            level = logging.INFO
        else:
            s = ' (there are some parsing errors)'
            level = logging.WARNING
        logger.log(level, 'Processing AST for %s%s.', rp, s)
        if diags:
            for diag in diags:
                d = get_diag_info(diag)
                logger.debug('%s', d)
        start = tu.cursor
        statics = 0
        for node in walk_ast(start):
            if not node.extent.start.file:
                fn = None
            else:
                fn = node.extent.start.file.name
            if os.name == 'nt':
                if fn:
                    fn = fn.replace(os.sep, '/')
                p = p.replace(os.sep, '/')
            if fn != p:
                continue
            if node.kind != CursorKind.VAR_DECL:
                continue
            if node.storage_class == StorageClass.EXTERN:
                continue
            if node.semantic_parent.kind == CursorKind.FUNCTION_DECL:
                if node.storage_class in (StorageClass.NONE,
                                          StorageClass.REGISTER):
                    continue
            ts = node.type.spelling
            if CONST_STRUCT_TYPES.match(ts):
                continue
            if IGNORED_STRUCT_TYPES.match(ts):
                continue
            if CONST_TYPES.search(ts):
                continue
            start = node.extent.start
            end = node.extent.end
            sc = node.storage_class
            sc = SCTEXT.get(sc, str(sc))
            loc = '(%d, %d) - (%d, %d)' % (start.line, start.column,
                                           end.line, end.column)
            register_static(options, node.spelling, sc, ts, rp, start.line,
                            start.column, end.line, end.column)
            statics += 1
            logger.debug('%-8s %-16s %s %s' % (sc, loc, ts, node.spelling))
        if statics:
            s = '' if statics == 1 else 's'
            logger.info('   %d static%s found.', statics, s)


def main():
    parser = argparse.ArgumentParser()
    aa = parser.add_argument
    aa('-c', '--compute-args', dest='compute_args',
       help='Compute parsing arguments from make commands in specified file')
    aa('-a', '--args', default='args.json',
       help='Parse Python C files using arguments in specified file')
    aa('-d', '--database', default='statics.sqlite',
       help='Write statics information to specified file')
    aa('-n', '--new', action='store_true', help='Create new statics database')
    aa('-p', '--python-dir', default=PYTHON_DIR, help='Python source location')
    aa('--clang-dir', default='/usr/lib/llvm-6.0/lib',
       help='Location of clang library (libclang)')
    options = parser.parse_args()
    logger.debug('options: %s', options)

    if options.compute_args:
        ca = compute_args_windows if os.name == 'nt' else compute_args_linux
        ca(options)
    else:
        compute_statics(options)


if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s',
                        filename='clang_analysis.log', filemode='w')
    h = logging.StreamHandler()
    h.setLevel(logging.INFO)
    logging.getLogger().addHandler(h)
    try:
        rc = main()
    except Exception as e:
        logger.exception('Failed: %s', e)
        rc = 1
    sys.exit(rc)
