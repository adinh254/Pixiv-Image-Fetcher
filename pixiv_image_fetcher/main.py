"""Module Testing"""
import getpass

from scrapy.crawler import CrawlerProcess

from pixiv_image_fetcher.spiders.bookmarks_spider import BookmarksSpider

def main():
    """Testing"""
    my_pixiv_id = input('Email/Pixiv ID: ')
    my_password = getpass.getpass()
    starting_page = input('Start Page: ')
    last_page = input('Last Page: ')
    process = CrawlerProcess()

    process.crawl(BookmarksSpider, pixiv_id=my_pixiv_id, password=my_password,
                  starting_page=starting_page, last_page=last_page)
    process.start()
if __name__ == '__main__':
    main()
