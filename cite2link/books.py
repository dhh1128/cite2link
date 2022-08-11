import re

defn_pat = re.compile(r'\s*([^:/]+)(?::\s*([A-Za-z- &]+))?(?:/\s*([1-4a-z]+))?\s*')


def _purify_name_chars(name):
    name = name.lower()
    return ''.join([c for c in name if c.isalpha() or c.isdigit()])


class Book:
    def __init__(self, defn, collection_key):
        # Associate the book with its parent collection
        self.collection_key = collection_key
        # Set defaults (may be overridden)
        self.chapter_and_verse = True
        self.unique = None
        self.abbrev = None
        # Strip off ordinal if applicable.
        if defn[0].isdigit():
            self.ordinal = defn[0]
            defn = defn[1:].lstrip()
        else:
            self.ordinal = None
        # Parse the rest of the expression
        m = defn_pat.match(defn)
        # If we've been given a precalculated string that's
        # the minimum prefix to make this name unique,
        # record that.
        if m.group(3):
            self.unique = m.group(3)
        # If we've been given a canonical abbreviation, record it.
        # This value can have punctuation, spaces, and capitals.
        ab = None
        if m.group(2):
            self.abbrev = m.group(2)
            ab = _purify_name_chars(self.abbrev)
            # If we didn't get unique, but we have an abbreviation,
            # use the abbreviation as our unique value.
            if not self.unique:
                self.unique = ab
        # Split all remaining names.
        names = m.group(1).split('|')
        # Notice if this is a book that doesn't have both chapter
        # and verse.
        if names[0].endswith('!'):
            self.chapter_and_verse = False
            names[0] = names[0][:-1]
        # Record the canonical title. This value can have spaces
        # and capitals.
        self.title = self.ordinal + ' ' + names[0] if self.ordinal else names[0]
        # Remove spaces, punct, and lower case all the names.
        self.names = [_purify_name_chars(item) for item in names]
        if ab and ab not in self.names:
            self.names.append(ab)
        # If we still didn't have a unique value, then use
        # the full name.
        if not self.unique:
            self.unique = self.names[0]
        # Get a list of all the characters that begin names of this book.
        # We will use this later to optimize lookups.
        self.first_chars = set([name[0] for name in self.names])

    @property
    def abbrev_title(self):
        if self.abbrev:
            return self.ordinal + ' ' + self.abbrev if self.ordinal else self.abbrev

    @property
    def unique_basis(self):
        return self.ordinal + self.names[0] if self.ordinal else self.names[0]

    @property
    def slug(self):
        return self.abbrev_title if self.abbrev_title else self.title

    def __str__(self):
        return self.slug


def load(collection_key, definitions):
    return [Book(item, collection_key) for item in definitions.split(',')]


# Define collections of books. Each item is in the format:
#       long name|alternate name|another alt:can/unique
# ...where long name is the preferred full form title, in its
# proper case, "can" means a canonical abbreviation, and "unique"
# means the shortest string that uniquely identifies the book
# in the corpus of all book names. If the first long name for
# a book ends with !, this means the book doesn't have
# both chapter and verse (it's cited with a single number).

old_testament = load('ot',
    'Genesis|gs|gn:Gen/ge,Exodus:Ex,Leviticus:Lev/le,Numbers|nbrs:Num/nu,Deuteronomy:Deut/de,Joshua:Josh,' +
    'Judges:Judg,Ruth/ru,1 Samuel:Sam/1sa,2 Samuel:Sam/2sa,1 Kings|kngs:Kgs/1ki,2 Kings|kngs:Kgs/2ki,' +
    '1 Chronicles|chrn:Chr/1ch,2 Chronicles|chrn:Chr/2ch,Ezra/ezr,Nehemiah:Neh/ne,Esther:Esth/es,Job,' +
    'Psalms|psal:Ps,Proverbs|prvbs|prvb:Prov/pr,Ecclesiastes:Eccl/ec,' +
    'Song of Solomon|songofsongs|canticles|cant|sos|ss:Song/so,Isaiah:Isa/is,Jeremiah:Jer/je,' +
    'Lamentations:Lam/la,Ezekiel:Ezek/eze,Daniel:Dan/da,Hosea/ho,Joel/joe,Amos/am,' +
    'Obadiah:Obad/ob,Jonah|jnh/jon,Micah/mi,Nahum/na,Habakkuk:Hab,Zephaniah:Zeph/zep,Haggai|hagai:Hag,' +
    'Zechariah:Zech/zec,Malachi:Mal')

new_testament = load('nt',
    'Matthew|mathew:Matt/mat,Mark/mar,Luke/lu,John/joh,Acts/ac,Romans:Rom/ro,1 Corinthians|crnth:Cor/1co,' +
    '2 Corinthians|crnth:Cor/2co,Galatians|gltn:Gal/ga,Ephesians|ephs:Eph/ep,Philippians|phlp|phillipians:Philip/phili,' +
    'Colossians|cls:Col/co,1 Thessalonians:Thes/1th,2 Thessalonians:Thes/2th,1 Timothy:Tim/1ti,2 Timothy:Tim/2ti,' +
    'Titus/ti,Philemon:Philem/phile,Hebrews:Heb,James/jam,1 Peter:Pet/1pe,2 Peter:Pet/2pe,1 John:Jn/1jo,' +
    '2 John:Jn/2jo,3 John:Jn/3jo,Jude,Revelation|apocalypse:Rev/re')

bible = [old_testament, new_testament]

book_of_mormon = load('bofm',
    '1 Nephi:Ne/1ne,2 Nephi:Ne/2ne,Jacob/jac,Enos/en,Jarom/jar,Omni/om,Words of Mormon|wm|wom:W of M/wo,' +
    'Mosiah/mosi,Alma/al,Helaman:Hel,3 Nephi:Ne/3ne,4 Nephi:Ne/4ne,Mormon:Morm,Ether/et,Moroni:Moro')

pearl_of_great_price = load('pgp',
    'Moses:Mos/mose,Abraham|abrhm|abrh:Abr/ab,Joseph Smith - Matthew|jsmatthew|jsm|jsmatt|jsmat:JS-M/josephsmithm,' +
    'Joseph Smith - History|jshistory|jsh|jshist|jshis:JS-H/josephsmithh,' +
    'Articles of Faith|artoffaith|artfaith|aof|af|aoff:A of F/ar')

doctrine_and_covenants = load('dc-testament',
    'Doctrine & Covenants|doctrineandcovenants|docandcov|dnc|d&c|dc:D&C/do,' +
    'Official Declaration!|offdec:OD/of')

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
    # If we wanted to optimize this, we could build a dict of lists of books,
    # indexed by the first letter of their names. This would allow us to skip
    # a lot of iteration. However, the optimization doesn't seem important
    # right now.
    for book in next_book(library):
        # First test: make sure both books lack an ordinal -- or that both
        # books have one, and the ordinals match.
        if named.ordinal == book.ordinal:
            # Second test: does name match the first letter of any variant of
            # this book's name? If no, there's no point in doing fancier
            # comparisons.
            if first_char in book.first_chars:
                # If we got an exact book name, it's a match.
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

