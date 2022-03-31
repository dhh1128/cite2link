import re

def transform(txt):
    return txt


scripture_ref_pat = re.compile(r"""
    (first|1(?:st)?|2(?:nd)?|third|3(?:rd)?|fourth|4(?:th)?)\s* # leading volume, cap group 1
    ([a-z ]+) # book/author, cap group 2
    \W*
    (\d+) # chapter (or item, for some sources), cap group 3
    ( # everything after chapter/item is optional
    \s*:\s*
    ([-0-9, ]+) # verses
    )? # end of optional part
    """, re.I | re.VERBOSE
)


word_splitter = re.compile(r'(\w)(\w*)(\W|$)')
def title_case(txt):
    capitalized = ''
    for m in word_splitter.finditer(txt):
        capitalized += m.group(1).upper() + m.group(2) + m.group(3)
    return capitalized.replace(' Of ', ' of ')

class Book:
    def __init__(self, txt):
        if txt[0].isdigit():
            self.ordinal = txt[0]
            txt = txt[2:]
        else:
            self.ordinal = None
        self.unique = None
        i = txt.find('/')
        if i > -1:
            self.unique = txt[i + 1:]
            txt = txt[:i]
        i = txt.find(':')
        self.abbrev = None
        if i > -1:
            self.abbrev = txt[i + 1:]
            txt = txt[:i]
            if not self.unique:
                self.unique = self.abbrev
        names = txt.split('|')
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

    @property
    def title(self):
        t = title_case(self.names[0])
        return self.ordinal + ' ' + t if self.ordinal else t


    @property
    def unique_basis(self):
        return self.ordinal + self.names[0] if self.ordinal else self.names[0]


def load(x):
    return [Book(item) for item in x.split(',')]


ot_books = load('genesis:gen/ge,exodus:ex,leviticus:lev/le,numbers:num/nu,deuteronomy:deut/de,joshua:josh,' +
    'judges:judg,ruth/ru,1 samuel:sam/1sa,2 samuel:sam/2sa,1 kings:kgs/1ki,2 kings:kgs/2ki,1 chronicles:chr/1ch,' +
    '2 chronicles:chr/2ch,ezra/ezr,nehemiah:neh/ne,esther:esth/es,job,psalms:ps,proverbs:prov/pr,' +
    'ecclesiastes:eccl/ec,song of solomon|song of songs|canticles:song/so,isaiah:isa/is,jeremiah:jer/je,' +
    'lamentations:lam/la,ezekiel:ezek/eze,daniel:dan/da,hosea/ho,joel/joe,amos/am,obadiah:obad/ob,jonah/jon,' +
    'micah/mi,nahum/na,habakkuk:hab,zephaniah:zeph/zep,haggai|hagai:hag,zechariah:zech/zec,malachi:mal')

nt_books = load('matthew:matt/mat,mark/mar,luke/lu,john/joh,acts/ac,romans:rom/ro,1 corinthians:cor/1co,' +
    '2 corinthians:cor/2co,galatians:gal/ga,ephesians:eph/ep,philippians|phillipians:philip/phili,' +
    'colossians:col/co,1 thessalonians:thes/1th,2 thessalonians:thes/2th,1 timothy:tim/1ti,2 timothy:tim/2ti,' +
    'titus/ti,philemon:philem/phile,hebrews:heb,james/jam,1 peter:pet/1pe,2 peter:pet/2pe,1 john:jn/1jo,' +
    '2 john:jn/2jo,3 john:jn/3jo,jude,revelation|apocalypse:rev/re')

bom_books = load('1 nephi:ne/1ne,2 nephi:ne/2ne,jacob/jac,enos/en,jarom/jar,omni/om,words of mormon/wo,' +
    'mosiah/mosi,alma/al,helaman:hel,3 nephi:ne/3ne,4 nephi:ne/4ne,mormon:morm,ether/et,moroni:moro')

pgp_books = load('moses:mos/mose,abraham:abr/ab,joseph smith-matthew:js-m/joseph smith-m,' +
    'joseph smith-history:js-h/joseph smith-h,articles of faith:a of f/ar')

all_books = [ot_books, nt_books, bom_books, pgp_books]

del load

def split_scripture_ref(ref):
    m = scripture_ref_pat.match(ref)
    if m:
        return m.group(1), m.group(2)
