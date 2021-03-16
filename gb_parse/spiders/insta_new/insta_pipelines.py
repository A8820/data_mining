# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class DefaultValuePipeline:
    def process_item(self, item, spider):
        """
        Set default values for the fields.
        """
        for field in item.fields:
            if field != '_id':
                item.setdefault(field, None)
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
        client = MongoClient()
        self.db = client['instagram']

    def process_item(self, item, spider):
        """
        Insert item into corresponding MongoDB collection.
        """
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item
