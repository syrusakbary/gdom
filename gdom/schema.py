import graphene
from pyquery import PyQuery as pq


class Node(graphene.Interface):
    '''A Node represents a DOM Node'''
    content = graphene.String(description='The html representation of the subnodes for the selected DOM',
                              selector=graphene.String())
    html = graphene.String(description='The html representation of the selected DOM',
                           selector=graphene.String())
    text = graphene.String(description='The text for the selected DOM',
                           selector=graphene.String())
    tag = graphene.String(description='The tag for the selected DOM',
                          selector=graphene.String())
    attr = graphene.String(description='The DOM attr of the Node',
                           selector=graphene.String(),
                           name=graphene.String().NonNull)
    _is = graphene.Boolean(description='Returns True if the DOM matches the selector',
                           name='is', selector=graphene.String().NonNull)
    query = graphene.List('Element',
                          description='Find elements using selector traversing down from self',
                          selector=graphene.String().NonNull)
    children = graphene.List('Element',
                             description='The list of children elements from self',
                             selector=graphene.String())
    parents = graphene.List('Element',
                            description='The list of parent elements from self',
                            selector=graphene.String())
    parent = graphene.Field('Element',
                            description='The parent element from self')
    siblings = graphene.List('Element',
                            description='The siblings elements from self',
                            selector=graphene.String())
    next = graphene.Field('Element',
                          description='The immediately following sibling from self',
                          selector=graphene.String())
    prev = graphene.Field('Element',
                          description='The immediately preceding sibling from self',
                          selector=graphene.String())

    def _query_selector(self, args):
        selector = args.get('selector')
        if not selector:
            return self._root
        return self._root.find(selector)

    def resolve_content(self, args, info):
        return self._query_selector(args).eq(0).html()

    def resolve_html(self, args, info):
        return self._query_selector(args).outerHtml()

    def resolve_text(self, args, info):
        return self._query_selector(args).eq(0).remove('script').text()

    def resolve_tag(self, args, info):
        el = self._query_selector(args).eq(0)
        if el:
            return el[0].tag

    def resolve__is(self, args, info):
        return self._root.is_(args.get('selector'))

    def resolve_attr(self, args, info):
        attr = args.get('name')
        return self._query_selector(args).attr(attr)

    def resolve_query(self, args, info):
        return self._query_selector(args).items()

    def resolve_children(self, args, info):
        selector = args.get('selector')
        return self._root.children(selector).items()

    def resolve_parents(self, args, info):
        selector = args.get('selector')
        return self._root.parents(selector).items()

    def resolve_parent(self, args, info):
        parent = self._root.parents().eq(-1)
        if parent:
            return parent

    def resolve_siblings(self, args, info):
        selector = args.get('selector')
        return self.siblings(selector).items()

    def resolve_next(self, args, info):
        selector = args.get('selector')
        n = self.nextAll(selector)
        if n:
            return n.eq(0)

    def resolve_prev(self, args, info):
        selector = args.get('selector')
        n = self.prevAll(selector)
        if n:
            return n.eq(0)


def get_page(page):
    return pq(page, headers={'user-agent': 'gdom'})


class Document(Node):
    '''
    The Document Type represent any web page loaded and
    serves as an entry point into the page content
    '''
    title = graphene.String(description='The title of the document')

    def resolve_title(self, args, info):
        return self._root.find('title').eq(0).text()


class Element(Node):
    '''
    A Element Type represents an object in a Document
    '''

    visit = graphene.Field(Document,
                           description='Visit will visit the href of the link and return the corresponding document')

    def resolve_visit(self, args, info):
        # If is a link we follow through href attr
        # return the resulting Document
        if self._root.is_('a'):
            href = self._root.attr('href')
            return get_page(href)


class Query(graphene.ObjectType):
    page = graphene.Field(Document,
                          description='Visit the specified page',
                          url=graphene.String(description='The url of the page'),
                          source=graphene.String(description='The source of the page'))

    def resolve_page(self, args, info):
        url = args.get('url')
        source = args.get('source')
        assert url or source, 'At least you have to provide url or source of the page'
        return get_page(url or source)


schema = graphene.Schema(query=Query)
schema.register(Element)
