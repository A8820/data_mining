"""
Источник:   https://www.instagram.com/
Задача:     На вход программе подяется 2 имени пользователя
            Найти самую короткую цепочку рукопожатий между этими пользователями.
            Рукопожатием считаем только взаимоподписанных пользовтаелей.
"""
import os

from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from insta_handshakes import InstaHandshakeSpider

# Get the login info.
load_dotenv('insta_handshakes.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule("gb_parse.settings")
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    # Get usernames for finding a handshake chain
    print("Enter usernames to find shortest handshake chain.")
    users = []
    for i in range(2):
        print(f"Username {i + 1}:")
        # users.append(input())
    users = []
    # Set the spider for crawling, pass login and enc_password login info to the spider.
    crawl_proc.crawl(
        InstaHandshakeSpider,
        users=users,
        login=os.getenv('LOGIN'),
        enc_password=os.getenv('ENC_PASSWORD')
    )
    crawl_proc.start()
