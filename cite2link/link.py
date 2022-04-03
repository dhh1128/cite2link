from .cite import join_nums_and_pairs

cojesuschrist_base = 'https://www.churchofjesuschrist.org/study/scriptures/'


def make_html_churchofjesuschrist(book, chapter, verses):
    book_slug = book.abbrev_title.replace(' ', '-')
    first_verse_item = verses[0]
    first_verse = first_verse_item if isinstance(first_verse_item, int) else first_verse_item[0]
    fragment = '#p%d' % first_verse - 1 if first_verse > 1 else ''
    verses = join_nums_and_pairs(verses, ',')
    return f'{cojesuschrist_base}{book.collection_key}/{book_slug}/{chapter}.{verses}?lang=eng{fragment}'
