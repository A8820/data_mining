"""
Источник:   https://www.instagram.com/
Задача:     Пройти по произвольному списку имен пользователей.
            Cобрать в единую структуру - на кого подписан пользователь и кто подписан на пользователя.
"""
import os

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.insta_new.instasub import InstaSubSpider

# Get the login info.
load_dotenv('instasub_env.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule("gb_parse.settings")
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # Set the spider for crawling, pass login and enc_password login info to the spider.
    crawl_proc.crawl(InstaSubSpider, login=os.getenv('LOGIN'), enc_password=os.getenv('ENC_PASSWORD'))
    crawl_proc.start()
