import scrapy

import bookmarks_spider

class TagSpider(bookmarks_spider.BookmarksSpider):
    name = "tags"