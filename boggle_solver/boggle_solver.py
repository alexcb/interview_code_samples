import random
import string
import collections


width = 4
height = 4
min_word_len=3
max_word_len=6


unlimited = object()
def read_dictionary_words(dictionary_filename, min_size=0, max_size=unlimited):
    words = set()
    for word in open(dictionary_filename):
        word = word.strip()
        if max_size == unlimited:
            if min_size <= len(word):
                words.add(word)
        elif min_size <= len(word) <= max_size:
            words.add(word)
    return words


def get_random_board(width, height):
    return ''.join(
        random.choice(string.ascii_lowercase)
        for _ in xrange(width*height))


# From http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


def potential_words(board, height, width, min_word_len, max_word_len):
    used_char_dice = [False] * (width*height)
    def potential_words_imp(row_start, row_end, col_start, col_end, prefix=''):
        if len(prefix) < max_word_len:
            for row in xrange(row_start, row_end):
                for col in xrange(col_start, col_end):
                    i = row*width + col
                    if not used_char_dice[i]:
                        word = prefix + board[i]
                        yield word
                        used_char_dice[i] = True
                        for x in potential_words_imp(
                                max(row-1, 0), min(row+2, height),
                                max(col-1, 0), min(col+2, width),
                                word):
                            yield x
                        used_char_dice[i] = False

    for x in potential_words_imp(0, width, 0, height):
        if len(x) >= min_word_len:
            yield x


# For the example, I found a txt file with english word, from:
#   http://www-01.sil.org/linguistics/wordlists/english/
# downloaded with:
#   curl http://www-01.sil.org/linguistics/wordlists/english/wordlist/wordsEn.txt | dos2unix > words_en.txt
words_set = read_dictionary_words('words_en.txt', min_size=min_word_len, max_size=max_word_len)
def is_word(word):
    return word in words_set


def find_words(board, height, width, min_word_len, max_word_len):
    return (
        x for x in potential_words(board, height, width, min_word_len, max_word_len)
        if is_word(x) )


def iter_len(iterable):
    count = 0
    for x in iterable:
        count += 1
    return count


def get_total_words(board, height, width, min_word_len, max_word_len):
    return iter_len(find_words(board, height, width, min_word_len, max_word_len))


def get_total_unique_words(board, height, width, min_word_len, max_word_len):
    return len(set(find_words(board, height, width, min_word_len, max_word_len)))


if __name__ == '__main__':
    board = get_random_board(width, height)
    
    print 'Random board is:'
    print '\n'.join(('  %s' % x for x in chunks(board, width)))
    print ''
    
    # Example of printing all words
    print 'All words:'
    for word in find_words(board, width, height, min_word_len, max_word_len):
        print '  %s' % word
    print ''

    # Example of only printing the count -- as per the original interview question
    # One thing we didn't discuss is that words may show up more than once in the board
    # Here's an example of both the totals including duplicate words as well as the unique totals
    print 'Totals:'
    print '  words: %s' % get_total_words(board, width, height, min_word_len, max_word_len)
    print '  unique words: %s' % get_total_unique_words(board, width, height, min_word_len, max_word_len)
    print ''

    # If we wanted to display all this information, one might simply create
    # a counter (dictionary-type interface) and make reference to it for displaying
    # totals (sum of values), unique totals (sum of keys), list of all words (keys), etc.
    # Here's some silly "interesting-facts" which make use of the collections.Counter
    print 'Interesting Facts'
    word_appearance_count = collections.Counter(
            find_words(board, width, height, min_word_len, max_word_len)
            )
    try:
        highest_occurrence = max(word_appearance_count.itervalues())
    except ValueError:
        print '  This board contains no words.'
    else:
        if highest_occurrence == 1:
            print '  No words appear more than once on the board.'
        else:
            print '  The following word(s) appeared the %d time(s): %s.' % (
                highest_occurrence,
                ', '.join(k for k, v in word_appearance_count.iteritems() if v == highest_occurrence)
                )

