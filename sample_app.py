from flask import Flask
from gdom.schema import schema
from flask_graphql import GraphQL

app = Flask(__name__)
app.debug = True

default_query = '''
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

GraphQL(app, schema=schema, default_query=default_query)


if __name__ == '__main__':
    app.run()
