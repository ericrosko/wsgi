#!/usr/bin/env python3

"""
Usage:
python3 -u bookapp.py
http://localhost:8080/
http://localhost:8080/book/id1
"""

import re
import traceback

from bookdb import BookDB

DB = BookDB()

def book(book_id):
    info = DB.title_info(book_id)

    try:
        return """
            <h2>{title}</h2>
            <p>{isbn}<p>
            <p>{publisher}</p>
            <p>{author}</p>
            """.format(
               title=info['title'],
               isbn=info['isbn'],
               publisher=info['publisher'],
               author=info['author']
            )
    except:
        raise NameError


def books():
    """
    handles /
    """
    all_books = DB.titles()
    body = ['<h1>My Bookshelf</h1>', '<ul>']
    item_template = '<li><a href="/book/{id}">{title}</a></li>'
    for book in all_books:
        body.append(item_template.format(**book))
    body.append('</ul>')

    return '\n'.join(body)


def resolve_path(path):
    print("resolve_path(path):"), path

    funcs = {
        '': books,
        'book': book,
    }

    # turns /book/id1 into ['book', 'id1']
    # turns / into ['']
    path = path.strip('/').split('/')

    func_name = path[0]
    args = path[1:]

    try:
        func = funcs[func_name]
    except KeyError:
        raise NameError

    return func, args


def application(environ, start_response):
    headers = [('Content-type', 'text/html')]
    # print('entering application func')
    path = environ.get('PATH_INFO', None)
    print("path:", path)

    try:
        if path is None:
            raise NameError
        func, args = resolve_path(path)
        body = func(*args)
        # body = "<h1>here is a body</h1>"
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = "<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = "<h1>Internal Server Error</h1>"
        print(traceback.format_exc())
    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
