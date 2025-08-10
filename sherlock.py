import math
import re
from collections import defaultdict, Counter

# Sample plaintext
TEXT1 = """when you have eliminated the impossible, whatever remains, however improbable,
must be the truth
"""


TEXT2 = """Crime is common. Logic is rare. Therefore it is upon the logic rather than
upon the crime that you should dwell.
"""


SERMON = """And seeing the multitudes, he went up into a mountain: and when he was set, his disciples came unto him:
And he opened his mouth, and taught them, saying,
Blessed are the poor in spirit: for theirs is the kingdom of heaven.
Blessed are they that mourn: for they shall be comforted.
Blessed are the meek: for they shall inherit the earth.
Blessed are they which do hunger and thirst after righteousness: for they shall be filled.
Blessed are the merciful: for they shall obtain mercy.
Blessed are the pure in heart: for they shall see God.
Blessed are the peacemakers: for they shall be called the children of God.
Blessed are they which are persecuted for righteousness' sake: for theirs is the kingdom
of heaven.
Blessed are ye, when men shall revile you, and persecute you, and shall say all manner of
evil against you falsely, for my sake.
Rejoice, and be exceeding glad: for great is your reward in heaven: for so persecuted
they the prophets which were before you.
Ye are the salt of the earth: but if the salt have lost his savour, wherewith shall it be
salted? it is thenceforth good for nothing, but to be cast out, and to be trodden under
foot of men.
Ye are the light of the world. A city that is set on an hill cannot be hid.
Neither do men light a candle, and put it under a bushel, but on a candlestick; and it
giveth light unto all that are in the house.
Let your light so shine before men, that they may see your good works, and glorify your
Father which is in heaven.
Think not that I am come to destroy the law, or the prophets: I am not come to destroy,
but to fulfil.
For verily I say unto you, Till heaven and earth pass, one jot or one tittle shall in no wise
pass from the law, till all be fulfilled.
Whosoever therefore shall break one of these least commandments, and shall teach men so, he
shall be called the least in the kingdom of heaven: but whosoever shall do and teach them, the same shall be called
great in the kingdom of heaven.
For I say unto you, That except your righteousness shall exceed the righteousness of the scribes
and Pharisees, ye shall in no case enter into the kingdom of heaven.
Ye have heard that it was said by them of old time, Thou shalt not kill; and whosoever shall kill shall be in danger of
the judgment:
But I say unto you, That whosoever is angry with his brother without a cause shall be in danger of the judgment: and
whosoever shall say to his brother, Raca, shall be in danger of the council: but whosoever shall say, Thou fool, shall
be in danger of hell fire.
Therefore if thou bring thy gift to the altar, and there rememberest that thy brother hath ought against thee;
Leave there thy gift before the altar, and go thy way; first be reconciled to thy brother, and then come and offer thy
gift.
Agree with thine adversary quickly, whiles thou art in the way with him; lest at any time the adversary deliver thee to
the judge, and the judge deliver thee to the officer, and thou be cast into prison.
Verily I say unto thee, Thou shalt by no means come out thence, till thou hast paid the uttermost farthing.
Ye have heard that it was said by them of old time, Thou shalt not commit adultery:
But I say unto you, That whosoever looketh on a woman to lust after her hath committed adultery with her already in his
heart.
And if thy right eye offend thee, pluck it out, and cast it from thee: for it is profitable for thee that one of thy
members should perish, and not that thy whole body should be cast into hell.
And if thy right hand offend thee, cut it off, and cast it from thee: for it is profitable for thee that one of thy
members should perish, and not that thy whole body should be cast into hell.
It hath been said, Whosoever shall put away his wife, let him give her a writing of divorcement:
But I say unto you, That whosoever shall put away his wife, saving for the cause of fornication, causeth her to commit
adultery: and whosoever shall marry her that is divorced committeth adultery.
Again, ye have heard that it hath been said by them of old time, Thou shalt not forswear thyself, but shalt perform unto
the Lord thine oaths:
But I say unto you, Swear not at all; neither by heaven; for it is God's throne:
Nor by the earth; for it is his footstool: neither by Jerusalem; for it is the city of the great King.
Neither shalt thou swear by thy head, because thou canst not make one hair white or black.
But let your communication be, Yea, yea; Nay, nay: for whatsoever is more than these cometh of evil.
Ye have heard that it hath been said, An eye for an eye, and a tooth for a tooth:
But I say unto you, That ye resist not evil: but whosoever shall smite thee on thy right cheek, turn to him the other
also.
And if any man will sue thee at the law, and take away thy coat, let him have thy cloke also.
And whosoever shall compel thee to go a mile, go with him twain.
Give to him that asketh thee, and from him that would borrow of thee turn not thou away.
Ye have heard that it hath been said, Thou shalt love thy neighbour, and hate thine enemy.
But I say unto you, Love your enemies, bless them that curse you, do good to them that hate you, and pray for them
which despitefully use you, and persecute you;
That ye may be the children of your Father which is in heaven: for he maketh his sun to rise on the evil and on the
good, and sendeth rain on the just and on the unjust.
For if ye love them which love you, what reward have ye? do not even the publicans the same?
And if ye salute your brethren only, what do ye more than others? do not even the publicans so?
Be ye therefore perfect, even as your Father which is in heaven is perfect."
"""

KW1 = "LOGIC"
KW2 = "DEDUCTION"
KW = "MATTHEWCHAPTERFIVE"


# We normalize the text by removing all non-letters and making all letters uppercase
def normalize(text):
    return "".join([str.upper(c) for c in text if str.isalpha(c)])


# We convert letters A-Z to number 0-25 and vice versa using built-in operators ord and chr
def char_to_num(c):
    assert ord("A") <= ord(c) <= ord("Z")
    return ord(c) - ord("A")


def num_to_char(n):
    assert 0 <= n < 26
    return chr(ord("A") + n)


# The "inverse" of a letter is the result of counting backwards the same number
# of letters as one would forward so that "A" <--> "Z", "B" <--> "Y" etc.  This
# will be useful when we want to reverse encryption.
def inverse(text):
    return "".join(num_to_char((26 - char_to_num(c)) % 26) for c in text)


# Caesar Cipher - rotate the alphabet
def caesar(ltr, text, encode=True):
    offset = char_to_num(ltr) if encode else char_to_num(inverse(ltr))
    return "".join([num_to_char((char_to_num(c) + offset) % 26) for c in normalize(text)])


# Vigenere Cipher - notice that if the keyword has length 1, what results is a Caesar cipher
def vigenere(key, text, encode=True):
    nkey = normalize(key) if encode else normalize(inverse(key))
    return "".join([caesar(nkey[i % len(nkey)], c) for i, c in enumerate(normalize(text))])


# Frequency Analysis

# we count each letter frm A-Z as a 26-element tuple
NORM_CTS = (820, 150, 280, 430, 1270, 220, 200, 610, 700, 15, 77, 400, 240, 670,
            750, 190, 10, 600, 630, 910, 280, 98, 240, 15, 200, 7)

NORM_LTRS = [chr(ord('A') + x) for x in sorted(range(len(NORM_CTS)), key=lambda i: NORM_CTS[i], reverse=True)]


def most_frequent(text, n):
    return tuple(x[0] for x in Counter(normalize(text)).most_common(n))


def overlap(ltrs):
    return len(set(ltrs).intersection(set(NORM_LTRS[:len(ltrs)])))

# metric 1: normalize the vectors and take L1 norm

def pct(cts):
    s = sum(cts)
    return tuple(math.floor(100 * (i/s)) for i in cts)


NORM_PCT = pct(NORM_CTS)


def dist_l1(cts):
    return sum(abs(x - y) for x, y in zip(NORM_PCT, pct(cts)))

def dist_l2(cts):
    return sum((x - y)**2 for x, y in zip(NORM_PCT, pct(cts)))

def rank_dist(c1, offset):
    f = [l[0] for l in Counter(c1).most_common()]
    return sum(1 if x in NORM_LTRS[:8] else 0 for x in c1)


def rotate(cts, idx):
    return tuple(cts[idx:] + cts[:idx])


def min_offset(text):
    ct = pct(counts(normalize(text)))
    dists = [dist_l1(rotate(ct, i)) for i in range(26)]
    return chr(ord("A") + dists.index(min(dists)))


def counts(text):
    return tuple(Counter(normalize(text))[num_to_char(i)] for i in range(26))


# Guess keyword used for encryption assuming you know the key length
def min_keyword(vtext, keylen):
    return "".join(min_offset(vtext[i::keylen]) for i in range(keylen))


# Finding the probable key length
def partition_with_overlap(lst, size, overlap):
    step = size - overlap
    return [lst[i:i + size] for i in range(0, len(lst) - overlap, step)]


def most_freq_trigrams(text):
    return Counter(partition_with_overlap(normalize(text), 3, 2))


def posns(text, substring):
    return [m.start() for m in re.finditer(substring, text)]


def original_txt(text, poslist):
    return [text[i: i + 3] for i in poslist]


def gaps(pv):
    return [pv[i + 1] - pv[i] for i in range(len(pv) - 1)]


def gap_gcd(pv):
    return math.gcd(*gaps(pv))


if __name__ == "main":
    print(normalize(TEXT1))
