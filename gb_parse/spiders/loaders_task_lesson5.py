import re
from scrapy import Selector
from scrapy.loader import ItemLoader

from itemloaders.processors import TakeFirst, MapCompose
from gb_parse.items_task_lesson5 import HHVacancyItem, HHCompanyItem


def get_specifications(itm):
    tag = Selector(text=itm)
    return {tag.xpath('//div[contains(@class, "AdvertSpecs_label")]/text()').get():
                tag.xpath('//div[contains(@class, "AdvertSpecs_data")]//text()').get()}


def get_specifications_out(data):
    result = {}
    for itm in data:
        result.update(itm)
    return result


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()


class HHCompanyLoader(ItemLoader):
    default_item_class = HHCompanyItem
    name_in = ''.join
    name_out = TakeFirst()
    web_site_out = TakeFirst()
    url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    # fields_of_activity_in = ''.join
    # fields_of_activity_out = TakeFirst()
