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
  page(url:"http://www.yelp.com/biz/amnesia-san-francisco") {
    title: text(selector:"h1")
    phone: text(selector:".biz-phone")
    address: text(selector:".address")
    sections: query(selector:".breadcrumbs--hierarchy a") {
      text
      url: attr(name:"href")
    }
    reviews: query(selector:"[itemprop=review]") {
      date: text(selector:".rating-qualifier")
      rating: attr(selector:"[itemprop=ratingValue]", name:"content")
      username: text(selector:".user-name a")
      comment: text(selector:"p")
    }
  }
}
'''.strip()


def run_test_server():
    app = Flask(__name__)
    app.debug = True

    blueprint = Blueprint('graphql', flask_graphql.__name__,
                          template_folder='templates',
                          static_url_path='/static/graphql',
                          static_folder='static/graphql/')

    app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema))
    app.add_url_rule('/', view_func=GraphiQLView.as_view('graphiql', default_query=SAMPLE_QUERY))

    app.register_blueprint(blueprint)

    import webbrowser
    webbrowser.open('http://localhost:5000/')

    app.run()


def parse(query, source, page):
    execution = schema.execute(query, args={'page': page, 'source': source})
    if execution.errors:
        raise Exception(execution.errors[0])
    return execution.data


def main():
    parser = argparse.ArgumentParser(description='Process some integers.')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('query', type=argparse.FileType('r'), nargs='?', help='The query file', default=None)
    group.add_argument('--test', action='store_true', default=False)

    parser.add_argument('page', metavar='PAGE', nargs='?', const=1, type=str, help='The pages to parse')

    parser.add_argument('--source', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout)

    args = parser.parse_args()

    if args.test:
        run_test_server()
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
