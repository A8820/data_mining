"""
Источник:   https://www.instagram.com/
Задача:     Задача авторизованным пользователем обойти список произвольных тегов и
            сохранить структуру Item, олицетворяющую сам Tag.

            Сохранить структуру данных поста, включая обход пагинации.

            Все структуры должны иметь следующий вид:
            - _id
            - date_parse (datetime) - время когда произошло создание структуры
            - data - данные, полученные от инстаграм

            Скачать изображения всех постов и сохранить на диск.
"""
import os

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.insta_new.insta import InstagramSpider

# Get the login info.
load_dotenv('insta_env.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule("gb_parse.settings")  # "gb_parse.settings"
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # Set the spider for crawling, pass login and enc_password login info to the spider.
    crawl_proc.crawl(InstagramSpider, login=os.getenv('INST_LOGIN'), enc_password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()
