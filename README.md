# GDOM

GDOM is the next generation of web-parsing, powered by `GraphQL`
syntax and the [Graphene framework](http://graphene-python.org).

Install it typing in your console:

```bash
pip install gdom
```

**DEMO**: [Try GDOM online](http://gdom.graphene-python.org/)


## Usage

You can either do `gdom --test` to start a test server for testing
queries or

```bash
gdom QUERY_FILE
```

This command will write in the standard output (or other output if specified
via `--output`) the resulting JSON.

Your `QUERY_FILE` could look similar to this:

```graphql
{
  page(url:"http://www.yelp.com/biz/amnesia-san-francisco") {
    title: text(selector:"h1")
    phone: text(selector:".biz-phone")
    address: text(selector:".address")
    reviews: query(selector:"[itemprop=review]") {
      username: text(selector:".user-name a")
      comment: text(selector:"p")
    }
  }
}
```


## Advanced usage

If you want to generalize your gdom query to any page, just rewrite your
query file adding the `$page` var. So should look to something like
this:

```graphql
query ($page: String) {
  page(url:$page) {
    # ...
  }
}
```

And then, query it like:

```bash
gdom QUERY_FILE http://www.yelp.com/biz/amnesia-san-francisco
```
