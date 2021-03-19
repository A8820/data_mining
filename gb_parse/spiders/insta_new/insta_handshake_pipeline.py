# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

from insta_handshake_item import InstaSHFollowItem


class DefaultValuePipeline:
    def process_item(self, item, spider):
        """
        Set default values for the fields.
        """
        for field in item.fields:
            if field != '_id':
                item.setdefault(field, None)
        return item


class HandshakePipeline:
    def process_item(self, item, spider):
        """
        Find shortest handshake chain for 2 Instagram users.
        """
        if isinstance(item, InstaSHFollowItem):
            if item['follows_name'] == spider.start_users[1]:
                for _ in range(10):
                    print('---------- CHAIN FOUND -----------')
                spider.crawler.stop()

        # 2nd user to reach with handshakes?
        # Or maybe just scan both at the same time.
        # spider.target_user
        # Possible MongoDB aggregation with $graphLookup:
        """
            {
              from: 'InstaSHFollowItem',
              startWith: '$user_name',
              connectFromField: 'follows_name',
              connectToField: 'user_name',
              as: 'follow_chain',
              maxDepth: 10,
              depthField: 'depth',
              restrictSearchWithMatch: {'user_name': {$ne: 'billieeilish'}}
            }
        """
        return item


class ImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        """
        Get image URLs from the Item and send a Request to download.
        'img' property can be a list or a single URL - so we make it a list to have same processing.
        """
        img_urls = item.get('img', [])
        if not isinstance(img_urls, list):
            img_urls = [img_urls]
        for url in img_urls:
            try:
                yield Request(url)
            except Exception as e:
                print(e)

    def item_completed(self, results, item, info):
        if item.get('img'):
            item['img'] = [result[1] for result in results if result[0]]
        return item


class MongoPipeline:
    def __init__(self):
        mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = mongo_client['gb_data_mining']

    def process_item(self, item, spider):
        """
        Insert item into corresponding MongoDB collection.
        """
        item_type = type(item).__name__
        collection = self.db[item_type]

        collection.insert_one(item)
        return item
