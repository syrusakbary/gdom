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
gdom QUERY_FILE http://news.ycombinator.com
```
