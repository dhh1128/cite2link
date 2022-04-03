import re

from .books import find_book


scripture_cite_pat = re.compile(r"""
    ((?:first|1(?:st)?|sec(?:ond)?|2(?:nd)?|third|3(?:rd)?|fourth|4(?:th)?)?\s* # leading volume
    (?:[a-z&.]+(?:\ +[a-z&.]+)*)) # book/author, cap group 1
    \W*
    (\d+) # chapter (or item, for some sources), cap group 2
    (?: # everything after chapter/item is optional
    \s*:\s*
    ([-0-9,\ ]+) # verses, cap group 3
    )? # end of optional part
    """, re.I | re.VERBOSE
)


def parse(ref):
    """
    See if a scriptural reference can be recognized as matching a standard format.
    If yes, return a tuple of (book_name, chapter, verses). If no, return None.
    This does syntactic analysis only; it makes no attempt to see if the book name
    is valid or the chapter and verse portion make sense. It is probably more common
    for external callers to use resolve() instead, as this does a book lookup.
    """
    m = scripture_cite_pat.match(ref)
    if m:
        return m.group(1), m.group(2), m.group(3)


def resolve(ref):
    """
    Given a reference, see if it can be resolved to something that our library knows about.
    If yes, return a tuple of (book, chapter, verses), where book is an actual Book object,
    and verses is an array of normalized ints and int pairs (ranges). If no, return None.
    """
    triple = parse(ref)
    if triple:
        book = find_book(triple[0])
        if book:
            return book, triple[1], normalize_verses(triple[2])


_verse_range_pat = re.compile(r'(\d+)-(\d+)')
_verse_splitter_pat = re.compile(r'[ ,]+')
_space_range_pat = re.compile(r' +-')
_range_space_pat = re.compile(r'- +')


def split_verses(verses):
    """
    Split on any runs of commas and spaces. Remove spaces.
    """
    verses = _verse_splitter_pat.split(_range_space_pat.sub('-', _space_range_pat.sub('-', verses)))
    return [v for v in verses if v]


def get_nums_and_pairs_from_verses_text(verses):
    """
    Given an array of strings that describe either individual verses
    or ranges of verses, return an array of corresponding ints and
    int pairs: '3','5', '7-10' --> [3,5,(7,10)]
    """
    items = []
    # Get components -- either individual verses, or verse ranges.
    # Convert them to integers or tuples that hold integer pairs.
    for item in verses:
        m = _verse_range_pat.match(item)
        if m:
            pair = (int(m.group(1)), int(m.group(2)))
            if pair[0] > pair[1]:
                raise Exception('Bad range "%s"; %s > %s.' % (item, m.group(1), m.group(2)))
            items.append(pair)
        else:
            items.append(int(item))
    return items


def join_nums_and_pairs(verses, joiner=', '):
    """
    Given an array of ints and int pairs, return a single string
    of individual verse numbers and verse ranges: [3,5,(7,10)] --> "3, 5, 7-10".
    """
    return joiner.join([str(x) if isinstance(x, int) else '%d-%d' % x for x in verses])


def normalize_verses(verses):
    """
    Put verses in a canonical format -- ordered, with no redundancies or overlaps,
    and with maximum use of ranges for terseness. Return an array of ints and
    int pairs. To convert to text, call join_nums_and_pairs().
    """
    verses = split_verses(verses)
    nums_and_pairs = get_nums_and_pairs_from_verses_text(verses)
    # Sort them.
    verses = sorted(nums_and_pairs, key=lambda x: x if isinstance(x, int) else x[0])
    # Now go through the verses and look for redundancies, overlaps, or
    # consecutive verses that should be ranges. Rewrite as needed.
    nums_and_pairs = []
    start = end = -1
    for item in verses:
        is_num = isinstance(item, int)
        new = item if is_num else item[0]
        # Do we have a gap in verses that justifies adding a new item to the normalized list?
        if (new > end + 1) or not nums_and_pairs:
            start = new
            if is_num:
                end = start
                nums_and_pairs.append(start)
            else:
                end = item[1]
                nums_and_pairs.append((start, end))
        else:
            extend = False
            prev = nums_and_pairs[-1]
            prev_is_num = isinstance(prev, int)
            # Do we have a value that's one bigger than the last verse we saw? This might be
            # relatively common; a citation might list verses like "1, 2-3" when it should give
            # a range "1-3".
            if new == end + 1:
                extend = True
            # What about an overlapping range?
            elif not is_num:
                if item[1] > end:
                    extend = True
            if extend:
                old_start = prev if prev_is_num else prev[0]
                nums_and_pairs[-1] = (old_start, new) if is_num else (old_start, item[1])
                end = nums_and_pairs[-1][1]
            # else this item is totally redundant
    return nums_and_pairs