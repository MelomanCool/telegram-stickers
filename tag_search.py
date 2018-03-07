from difflib import SequenceMatcher
from operator import itemgetter
from typing import List

from model import TaggedSticker


def string_similarity(first, second):
    """Returns the degree of similarity between two strings"""

    return SequenceMatcher(a=first, b=second).ratio()


def tags_similarity(left_tags, right_tags, cutoff=0.6):
    if not (0 <= cutoff <= 1):
        raise ValueError('cutoff should be between 0 and 1')

    score = 0
    for left_tag in left_tags:
        # adding degree of similarity of the most similar tag
        most_similar_similarity = max(string_similarity(left_tag, right_tag) for right_tag in right_tags)
        if most_similar_similarity > cutoff:
            score += most_similar_similarity

    return score / len(left_tags)


def find_stickers(query_tags, tagged_stickers: List[TaggedSticker]):
    sticker_scores = [(tags_similarity(query_tags, sticker.tags), sticker)
                      for sticker in tagged_stickers]
    sticker_scores = [(score, sticker)
                      for score, sticker in sticker_scores
                      if score > 0]
    sticker_scores.sort(key=itemgetter(0), reverse=True)

    tagged_stickers = [sticker for score, sticker in sticker_scores]
    return tagged_stickers
