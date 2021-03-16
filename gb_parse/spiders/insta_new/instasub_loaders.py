# Define your item loaders here

from itemloaders.processors import TakeFirst, MapCompose
from scrapy.loader import ItemLoader

from instasub_item import (
    InstaSubFollowItem, InstaSubUserItem, InstaSubHashtagItem, InstaSubPostItem
)


def clean_whitespace(item):
    return item.replace(u'\xa0', '')


def insta_remove_user_waste(item):
    fields = ['id', 'username', 'full_name', 'profile_pic_url', 'is_private', 'is_verified']
    return {field: item[field] for field in fields}


class InstaSubLoader(ItemLoader):
    """
    Loader for Instagram Items.
    """
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstaSubFollowLoader(InstaSubLoader):
    """
    Loader for InstagramFollowItem.
    """
    default_item_class = InstaSubFollowItem


class InstaSubUserLoader(InstaSubLoader):
    """
    Loader for InstagramUserItem.
    """
    default_item_class = InstaSubUserItem
    data_in = MapCompose(insta_remove_user_waste)


class InstaSubHashtagLoader(InstaSubLoader):
    """
    Loader for InstagramHashtagItem.
    """
    default_item_class = InstaSubHashtagItem


class InstaSubPostLoader(InstaSubLoader):
    """
    Loader for InstagramPostItem.
    """
    default_item_class = InstaSubPostItem

    # name_out = ''.join
    # description_out = ''.join
    # website_url_out = TakeFirst()
    # employer_url_out = TakeFirst()
