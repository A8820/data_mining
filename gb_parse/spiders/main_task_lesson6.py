import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.task_lesson6 import InstagramSpider_

if __name__ == '__main__':
    dotenv.load_dotenv('.env')
    hash_tags = ['cats']
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramSpider_,
                     tags=hash_tags,
                     login=os.getenv('INST_LOGIN'),
                     enc_password=os.getenv('INST_PASSWORD'))
    crawl_proc.start()
