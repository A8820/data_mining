# Define your item loaders here

from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

from insta_handshake_item import (
    InstaSHItem, InstaSHFollowItem,
    InstaSHUserItem, InstaSHHashtagItem, InstaSHPostItem,
)


def clean_whitespace(item):
    return item.replace(u'\xa0', '')


def insta_remove_user_waste(item):
    fields = ['id', 'username', 'full_name', 'profile_pic_url', 'is_private', 'is_verified']
    return {field: item[field] for field in fields}


class InstaSHLoader(ItemLoader):
    """
    Loader for Instagram Items.
    """
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstaSHUserLoader(InstaSHLoader):
    """
    Loader for InstagramUserItem.
    """
    default_item_class = InstaSHItem
    data_in = MapCompose(insta_remove_user_waste)


class InstaSHHashtagLoader(InstaSHLoader):
    """
    Loader for InstagramHashtagItem.
    """
    default_item_class = InstaSHHashtagItem


class InstaSHPostLoader(InstaSHLoader):
    """
    Loader for InstagramPostItem.
    """
    default_item_class = InstaSHItem
