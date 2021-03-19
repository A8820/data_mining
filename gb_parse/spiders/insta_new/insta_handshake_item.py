# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaSHItem(scrapy.Item):
    """
    Base Item for Instagram structures.
    Attributes:
    - date_parse (datetime) - datetime when Item was created.
    - data - data received from Instagram about the hashtag.
    """
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstaSHFollowItem(scrapy.Item):
    """
    Item for an Instagram follower.
    """
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follows_id = scrapy.Field()
    follows_name = scrapy.Field()


class InstaSHUserItem(InstaSHItem):
    """
    Item for an Instagram user.
    """
    pass


class InstaSHHashtagItem(InstaSHItem):
    """
    Item for an Instagram hashtag.
    """
    pass


class InstaSHPostItem(InstaSHItem):
    """
    Item for an Instagram hashtag.
    """
    pass
