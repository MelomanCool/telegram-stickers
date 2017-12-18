from collections import namedtuple

from .sticker import Sticker


TaggedSticker = namedtuple('TaggedSticker', Sticker._fields + ('tags',))
