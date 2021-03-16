# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
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


class InstagramHashtagItem(InstagramItem):
    """
    Item for an Instagram hashtag.
    - _id - field for MongoDB to write its ID in.
            Not in parent class InstagramItem, because it would be a protected attribute.
    """
    pass


class InstagramPostItem(InstagramItem):
    """
    Item for an Instagram hashtag.
    - _id - field for MongoDB to write its ID in.
            Not in parent class InstagramItem, because it would be a protected attribute.
    """
    pass
