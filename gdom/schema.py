import graphene
from pyquery import PyQuery as pq


def _query_selector(pq, selector):
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
                           name=graphene.String(required=True))
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

    def resolve_content(self, info, selector):
        return _query_selector(self, selector).eq(0).html()

    def resolve_html(self, info, selector):
        return _query_selector(self, selector).outerHtml()

    def resolve_text(self, info, selector):
        return _query_selector(self, selector).eq(0).remove('script').text()

    def resolve_tag(self, info, selector):
        el = _query_selector(self, selector).eq(0)
        if el:
            return el[0].tag

    def resolve__is(self, info, selector=None):
        return self.is_(selector)

    def resolve_attr(self, info, name, selector=None):
        return _query_selector(self, selector).attr(name)

    def resolve_query(self, info, selector=None):
        return _query_selector(self, selector).items()

    def resolve_children(self, info, selector=None):
        return self.children(selector).items()

    def resolve_parents(self, info, selector=None):
        return self.parents(selector).items()

    def resolve_parent(self, info):
        parent = self.parents().eq(-1)
        if parent:
            return parent

    def resolve_siblings(self, info, selector=None):
        return self.siblings(selector).items()

    def resolve_next(self, info, selector=None):
        _next = self.nextAll(selector)
        if _next:
            return _next.eq(0)

    def resolve_next_all(self, info, selector=None):
        return self.nextAll(selector).items()

    def resolve_prev(self, info, selector=None):
        prev = self.prevAll(selector)
        if prev:
            return prev.eq(0)

    def resolve_prev_all(self, info, selector=None):
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
    def is_type_of(cls, root, info):
        return isinstance(root, pq) or super(Document, cls).is_type_of(root, info)

    def resolve_title(self, info):
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
    def is_type_of(cls, root, info):
        return isinstance(root, pq) or super(Element, cls).is_type_of(root, info)

    def resolve_visit(self, info):
        # If is a link we follow through href attr
        # return the resulting Document
        if self.is_('a'):
            href = self.attr('href')
            return get_page(href)


class Query(graphene.ObjectType):
    page = graphene.Field(Document,
                          description='Visit the specified page',
                          url=graphene.String(
                              description='The url of the page'),
                          _source=graphene.String(
                              name='source', description='The source of the page')
                          )

    def resolve_page(self, info, url=None, source=None):
        assert url or source, 'At least you have to provide url or source of the page'
        return get_page(url or source)


schema = graphene.Schema(query=Query, types=[Element])
