# Define your item loaders here

from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader

from gb_parse.spiders.insta_new.insta_item import (
    InstagramHashtagItem, InstagramPostItem,
)


def clean_whitespace(item):
    return item.replace(u'\xa0', '')


class InstagramLoader(ItemLoader):
    """
    Loader for Instagram Items.
    """
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstagramHashtagLoader(InstagramLoader):
    """
    Loader for InstagramHashtagItem.
    """
    default_item_class = InstagramHashtagItem


class InstagramPostLoader(InstagramLoader):
    """
    Loader for InstagramPostItem.
    """
    default_item_class = InstagramPostItem
