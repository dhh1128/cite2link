from .cite import join_nums_and_pairs


cojesuschrist_base = 'https://www.churchofjesuschrist.org/study/scriptures/'


def embed_html(ref, inner):
    return f'<a href="{ref}">{inner}</a>'


def embed_markdown(ref, inner):
    return f'[{inner}]({ref})'


def make_churchofjesuschrist(book, chapter, verses):
    book_slug = book.slug.lower().replace(' ', '-').replace('&', '')
    if verses:
        first_verse_item = verses[0]
        first_verse = first_verse_item if isinstance(first_verse_item, int) else first_verse_item[0]
        fragment = '#p%d' % (first_verse - 1) if first_verse > 1 else ''
        verses = '.' + join_nums_and_pairs(verses, ',')
    else:
        verses = fragment = ''
    return f'{cojesuschrist_base}{book.collection_key}/{book_slug}/{chapter}{verses}?lang=eng{fragment}'


def make_short_ref(book, chapter, verses):
    verses = ':' + join_nums_and_pairs(verses, ', ') if verses else ''
    return f'{book.slug} {chapter}{verses}'


def make_long_ref(book, chapter, verses):
    verses = ':' + join_nums_and_pairs(verses, ', ') if verses else ''
    return f'{book.title} {chapter}{verses}'


# ------------ keep this block vvv at the bottom of the module --------------

# We want this at the bottom of the module because it uses python reflection
# to scan all the code that precedes it, and builds a list of all the functions
# that match a certain pattern. This allows us to add new citation styles by
# simply adding the relevant functions above, without manually updating a list
# of the styles we have.
g = globals()
all_makers = [key for key in g.keys() if key.startswith('make_') and callable(g[key])]
del g


def print_all(book, chapter, verses):
    g = globals()
    for key in all_makers:
        print(key[5:].replace('_', ' '))
        func = g[key]
        print('  %s\n' % func(book, chapter, verses))

    print('html\n  ' + embed_html(make_churchofjesuschrist(book, chapter, verses),
                                  make_short_ref(book, chapter, verses)) + '\n')
    print('markdown\n  ' + embed_markdown(make_churchofjesuschrist(book, chapter, verses),
                                  make_short_ref(book, chapter, verses)) + '\n')

# ------------ keep this block ^^^ at the bottom of the module --------------
