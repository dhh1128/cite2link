from .cite import join_nums_and_pairs

cojesuschrist_base = 'https://www.churchofjesuschrist.org/study/scriptures/'


def make_churchofjesuschrist(book, chapter, verses):
    book_slug = book.abbrev_title.lower().replace(' ', '-').replace('&', '')
    if verses:
        first_verse_item = verses[0]
        first_verse = first_verse_item if isinstance(first_verse_item, int) else first_verse_item[0]
        fragment = '#p%d' % (first_verse - 1) if first_verse > 1 else ''
        verses = '.' + join_nums_and_pairs(verses, ',')
    else:
        verses = fragment = ''
    return f'{cojesuschrist_base}{book.collection_key}/{book_slug}/{chapter}{verses}?lang=eng{fragment}'


def make_abbrev_ref(book, chapter, verses):
    verses = ':' + join_nums_and_pairs(verses, ', ') if verses else ''
    return f'{book.abbrev_title} {chapter}{verses}'


def make_long_ref(book, chapter, verses):
    verses = ':' + join_nums_and_pairs(verses, ', ') if verses else ''
    return f'{book.title} {chapter}{verses}'