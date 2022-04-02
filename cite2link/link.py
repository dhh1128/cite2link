
def make_churchofjesuschrist(book, chapter, verses):
    book_slug = '%s-%s' % (book.ordinal, book.abbrev) if book.ordinal else book.abbrev
    parent_slug = 'ot'
    return f'https://www.churchofjesuschrist.org/study/scriptures/{parent_slug}/{book_slug}/{chapter}/{verses}'
