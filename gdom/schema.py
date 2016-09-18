import graphene
from pyquery import PyQuery as pq


def _query_selector(pq, args):
    selector = args.get('selector')
    if not selector:
        return pq
    return pq.find(selector)


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
                           _name=graphene.String(name='name', required=True))
    _is = graphene.Boolean(description='Returns True if the DOM matches the selector',
                           name='is', selector=graphene.String(required=True))
    query = graphene.List(lambda: Element,
                          description='Find elements using selector traversing down from self',
                          selector=graphene.String(required=True))
    children = graphene.List(lambda: Element,
                             description='The list of children elements from self',
                             selector=graphene.String())
    parents = graphene.List(lambda: Element,
                            description='The list of parent elements from self',
                            selector=graphene.String())
    parent = graphene.Field(lambda: Element,
                            description='The parent element from self')
    siblings = graphene.List(lambda: Element,
                             description='The siblings elements from self',
                             selector=graphene.String())
    next = graphene.Field(lambda: Element,
                          description='The immediately following sibling from self',
                          selector=graphene.String())
    next_all = graphene.List(lambda: Element,
                             description='The list of following siblings from self',
                             selector=graphene.String())
    prev = graphene.Field(lambda: Element,
                          description='The immediately preceding sibling from self',
                          selector=graphene.String())
    prev_all = graphene.List(lambda: Element,
                             description='The list of preceding siblings from self',
                             selector=graphene.String())

    def resolve_content(self, args, context, info):
        return _query_selector(self, args).eq(0).html()

    def resolve_html(self, args, context, info):
        return _query_selector(self, args).outerHtml()

    def resolve_text(self, args, context, info):
        return _query_selector(self, args).eq(0).remove('script').text()

    def resolve_tag(self, args, context, info):
        el = _query_selector(self, args).eq(0)
        if el:
            return el[0].tag

    def resolve__is(self, args, context, info):
        return self.is_(args.get('selector'))

    def resolve_attr(self, args, context, info):
        attr = args.get('name')
        return _query_selector(self, args).attr(attr)

    def resolve_query(self, args, context, info):
        return _query_selector(self, args).items()

    def resolve_children(self, args, context, info):
        selector = args.get('selector')
        return self.children(selector).items()

    def resolve_parents(self, args, context, info):
        selector = args.get('selector')
        return self.parents(selector).items()

    def resolve_parent(self, args, context, info):
        parent = self.parents().eq(-1)
        if parent:
            return parent

    def resolve_siblings(self, args, context, info):
        selector = args.get('selector')
        return self.siblings(selector).items()

    def resolve_next(self, args, context, info):
        selector = args.get('selector')
        _next = self.nextAll(selector)
        if _next:
            return _next.eq(0)

    def resolve_next_all(self, args, context, info):
        selector = args.get('selector')
        return self.nextAll(selector).items()

    def resolve_prev(self, args, context, info):
        selector = args.get('selector')
        prev = self.prevAll(selector)
        if prev:
            return prev.eq(0)

    def resolve_prev_all(self, args, context, info):
        selector = args.get('selector')
        return self.prevAll(selector).items()


def get_page(page):
    return pq(page, headers={'user-agent': 'gdom'})


class Document(graphene.ObjectType):
    '''
    The Document Type represent any web page loaded and
    serves as an entry point into the page content
    '''
    class Meta:
        interfaces = (Node, )

    title = graphene.String(description='The title of the document')

    @classmethod
    def is_type_of(cls, root, context, info):
        return isinstance(root, pq) or super(Document, cls).is_type_of(root, context, info)

    def resolve_title(self, args, context, info):
        return self.find('title').eq(0).text()


class Element(graphene.ObjectType):
    '''
    A Element Type represents an object in a Document
    '''
    class Meta:
        interfaces = (Node, )

    visit = graphene.Field(Document,
                           description='Visit will visit the href of the link and return the corresponding document')

    @classmethod
    def is_type_of(cls, root, context, info):
        return isinstance(root, pq) or super(Element, cls).is_type_of(root, context, info)

    def resolve_visit(self, args, context, info):
        # If is a link we follow through href attr
        # return the resulting Document
        if self.is_('a'):
            href = self.attr('href')
            return get_page(href)


class Query(graphene.ObjectType):
    page = graphene.Field(Document,
                          description='Visit the specified page',
                          url=graphene.String(description='The url of the page'),
                          _source=graphene.String(name='source', description='The source of the page')
                          )

    def resolve_page(self, args, context, info):
        url = args.get('url')
        source = args.get('source')
        assert url or source, 'At least you have to provide url or source of the page'
        return get_page(url or source)


schema = graphene.Schema(query=Query, types=[Element])
