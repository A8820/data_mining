from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.task_lesson4 import AutoyoulaSpider_

if __name__ == "__main__":
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(AutoyoulaSpider_)
    crawler_proc.start()
