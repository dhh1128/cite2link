import re


_word_splitter = re.compile(r'(\w)(\w*)(\W|$)')


def _title_case(txt):
    capitalized = ''
    for m in _word_splitter.finditer(txt):
        capitalized += m.group(1).upper() + m.group(2) + m.group(3)
    return capitalized.replace(' Of ', ' of ').replace(' And ', ' and ')


class Book:
    def __init__(self, definition, collection_key):
        self.collection_key = collection_key
        self.chapter_and_verse = True
        definition = definition.lower().strip()
        if definition[0].isdigit():
            self.ordinal = definition[0]
            definition = definition[1:].lstrip()
        else:
            self.ordinal = None
        self.unique = None
        i = definition.find('/')
        if i > -1:
            self.unique = definition[i + 1:]
            definition = definition[:i]
        i = definition.find(':')
        self.abbrev = None
        if i > -1:
            self.abbrev = definition[i + 1:]
            definition = definition[:i]
            if not self.unique:
                self.unique = self.abbrev
        names = definition.replace('.', '').split('|')
        if names[0].endswith('!'):
            self.chapter_and_verse = False
            names[0] = names[0][:-1]
        self.names = names[:]
        if not self.unique:
            self.unique = names[0]
        for v in names:
            i = v.find(' ')
            if i > -1:
                words = v.split(' ')
                acronym = ''.join([w[0] for w in words])
                if acronym not in self.names:
                    self.names.append(acronym)
        self.first_chars = set([x[0] for x in self.names])

    @property
    def title(self):
        t = _title_case(self.names[0])
        return self.ordinal + ' ' + t if self.ordinal else t

    @property
    def abbrev_title(self):
        t = self.abbrev[0].upper() + self.abbrev[1:]
        return self.ordinal + ' ' + t if self.ordinal else t

    @property
    def unique_basis(self):
        return self.ordinal + self.names[0] if self.ordinal else self.names[0]

    def __str(self):
        return self.title


def load(collection_key, definitions):
    return [Book(item, collection_key) for item in definitions.split(',')]


# Define collections of books. Each item is in the format:
#       long name|alternate name|another alt:can/unique
# ...where "can" means a canonical abbreviation, and "unique"
# means the shortest string that uniquely identifies the book
# in the corpus of all book names. If the first long name for
# a book ends with !, this means the book doesn't have
# both chapter and verse (it's cited with a single number).

old_testament = load('ot', 'genesis:gen/ge,exodus:ex,leviticus:lev/le,numbers:num/nu,deuteronomy:deut/de,joshua:josh,' +
    'judges:judg,ruth/ru,1 samuel:sam/1sa,2 samuel:sam/2sa,1 kings:kgs/1ki,2 kings:kgs/2ki,1 chronicles:chr/1ch,' +
    '2 chronicles:chr/2ch,ezra/ezr,nehemiah:neh/ne,esther:esth/es,job,psalms:ps,proverbs:prov/pr,' +
    'ecclesiastes:eccl/ec,song of solomon|song of songs|canticles:song/so,isaiah:isa/is,jeremiah:jer/je,' +
    'lamentations:lam/la,ezekiel:ezek/eze,daniel:dan/da,hosea/ho,joel/joe,amos/am,obadiah:obad/ob,jonah/jon,' +
    'micah/mi,nahum/na,habakkuk:hab,zephaniah:zeph/zep,haggai|hagai:hag,zechariah:zech/zec,malachi:mal')

new_testament = load('nt', 'matthew:matt/mat,mark/mar,luke/lu,john/joh,acts/ac,romans:rom/ro,1 corinthians:cor/1co,' +
    '2 corinthians:cor/2co,galatians:gal/ga,ephesians:eph/ep,philippians|phillipians:philip/phili,' +
    'colossians:col/co,1 thessalonians:thes/1th,2 thessalonians:thes/2th,1 timothy:tim/1ti,2 timothy:tim/2ti,' +
    'titus/ti,philemon:philem/phile,hebrews:heb,james/jam,1 peter:pet/1pe,2 peter:pet/2pe,1 john:jn/1jo,' +
    '2 john:jn/2jo,3 john:jn/3jo,jude,revelation|apocalypse:rev/re')

bible = [old_testament, new_testament]

book_of_mormon = load('bom', '1 nephi:ne/1ne,2 nephi:ne/2ne,jacob/jac,enos/en,jarom/jar,omni/om,words of mormon/wo,' +
    'mosiah/mosi,alma/al,helaman:hel,3 nephi:ne/3ne,4 nephi:ne/4ne,mormon:morm,ether/et,moroni:moro')

pearl_of_great_price = load('pgp',
    'moses:mos/mose,abraham:abr/ab,joseph smith-matthew|jsm|jsmatthew|jsmatt|js-matthew:js-m/joseph smith-m,' +
    'joseph smith-history|jsh|jshistory|jshist|js-history:js-h/joseph smith-h,articles of faith!|art of faith|art faith|af:a of f/ar')

doctrine_and_covenants = load('dc', 'doctrine and covenants|doctrine & covenants|dc:d&c/do,official declaration!/of')

quad = [bible, book_of_mormon, doctrine_and_covenants, pearl_of_great_price]

library = quad

del load


def normalize_ordinal(ordinal):
    """
    Given a string like "first" or "1st" or "1", return the canonical version ('1').
    """
    return ordinal[0] if ordinal[0].isdigit() else str('ieho'.index(ordinal[1].lower()) + 1)


_lead_ordinal_pat = re.compile(r'(first|1(?:st)?|sec(?:ond)?|2(?:nd)?|third|3(?:rd)?|fourth|4(?:th)?)\s*(.*)', re.I)


def find_book(book_name_in_ref):
    """
    Look through all known books and find one that matches the given book name.
    Do fuzzy matching. Return the matching book if found, else None.
    """
    # Normalize punctuation in what we were given.
    if '&' in book_name_in_ref:
        book_name_in_ref = book_name_in_ref.replace(
            '&amp;', '&').replace(
            '&mdash;','-').replace(
            '&#151;', '-').replace(
            '&ndash;', '-').replace(
            '&#150;', '-')
    # Normalize stuff like "First Chron" and "3rd Esdras"
    m = _lead_ordinal_pat.match(book_name_in_ref)
    if m: # Transform into "1 Chron" or "3 Esdras" for lookup
        book_name_in_ref = normalize_ordinal(m.group(1)) + m.group(2)
    named = Book(book_name_in_ref, '')       # imagine book_name_in_ref = "1 Chron."
    name = named.names[0]                    # "chron"
    first_char = name[0]
    for book in next_book(library):
        # First test: make sure both books lack an ordinal -- or that both
        # books have one, and the ordinals match.
        if named.ordinal == book.ordinal:
            # Second test: does name match the first letter of any variant of
            # this book's name? If no, there's no point in doing fancier
            # comparisons.
            if first_char in book.first_chars:
                # If we got a canonical abbreviation, it's a match.
                if name == book.abbrev:
                    return book
                # If we got an exact book name, it's a match, too.
                for n in book.names:
                    if name == n:
                        return book
                # Do we have an unfamiliar short form (e.g., "Genes" for "Genesis")?
                x = len(named.unique_basis)
                if x >= len(book.unique) and named.unique_basis.startswith(book.unique):
                    # We now know that the referenced book has a name that starts with the string that
                    # uniquely identifies a particular book in our library. However, what if our reference
                    # differs from this unique value later on? For example, "ge" uniquely identifies
                    # genesis. If we get a reference to a book named "gesture", we don't want to match.
                    if named.unique_basis == book.unique_basis[:x]:
                        return book
                    # If we get here, we definitely won't find another match, because we've found that
                    # our string matched something unique to one of the books in our library -- yet didn't
                    # match it all the way. We can abort our loop and just return None.
                    return


def next_book(container):
    """
    Yield all individual books in a list or list of lists or similar.
    """
    for item in container:
        if isinstance(item, Book):
            yield item
        else:
            # Recurse
            for book in next_book(item):
                yield book
