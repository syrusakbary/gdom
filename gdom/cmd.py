import argparse
import json
import sys

import flask_graphql
from flask import Flask, Blueprint
from flask_graphql.graphiqlview import GraphiQLView
from flask_graphql.graphqlview import GraphQLView

from schema import schema

SAMPLE_QUERY = '''
{
  page(url:"http://news.ycombinator.com") {
    items: query(selector:"tr.athing") {
      rank: text(selector:"td span.rank")
      title: text(selector:"td.title a")
      sitebit: text(selector:"span.comhead a")
      url: attr(selector:"td.title a", name:"href")
      attrs: next {
         score: text(selector:"span.score")
         user: text(selector:"a:eq(0)")
         comments: text(selector:"a:eq(2)")
      }
    }
  }
}
'''.strip()


def get_test_app():
    app = Flask(__name__)
    app.debug = True

    blueprint = Blueprint('graphql', flask_graphql.__name__,
                          template_folder='templates',
                          static_url_path='/static/graphql',
                          static_folder='static/graphql/')

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema))
    app.add_url_rule('/', view_func=GraphiQLView.as_view('graphiql', default_query=SAMPLE_QUERY))

    app.register_blueprint(blueprint)

    return app


def parse(query, source, page):
    execution = schema.execute(query, args={'page': page, 'source': source})
    if execution.errors:
        raise Exception(execution.errors[0])
    return execution.data


def main():
    parser = argparse.ArgumentParser(description='Parse and scrape any web page using GraphQL queries')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query', type=argparse.FileType('r'), nargs='?', help='The query file', default=None)
    group.add_argument('--test', action='store_true', default=False, help='This will start a test server with a UI for querying')

    parser.add_argument('page', metavar='PAGE', nargs='?', const=1, type=str, help='The pages to parse')

    parser.add_argument('--source', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()

    if args.test:
        app = get_test_app()
        import webbrowser
        webbrowser.open('http://localhost:5000/')

        app.run()
    else:
        query = args.query.read()
        page = args.page
        if not sys.stdin.isatty():
            source = args.source.read()
        else:
            source = None
        data = parse(query, source, page)
        outdata = json.dumps(data, indent=4, separators=(',', ': '))
        args.output.write(outdata)
        args.output.write('\n')

if __name__ == '__main__':
    main()
