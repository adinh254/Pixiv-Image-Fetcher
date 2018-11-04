# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

"""Overload default file pipeline

Only saves jpgs and pngs
"""
import os.path
import logging

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem

LOGGER = logging.getLogger(__name__)

class PixivImagePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        """Overriden for Exception Handling"""
        try:
            request_meta = {
                'user_id' : item['user_id'],
                'artist_id' : item['artist_id'],
                'illust_id' : item['illust_id'],
            }
            if len(item['image_urls']) > 1:
                request_meta['album'] = True
            for image_num, image_url in enumerate(item['image_urls']):
                request_meta['image_num'] = image_num
                yield scrapy.Request(url=image_url,
                                     headers={
                                         'referer': item['referer']
                                     },
                                     meta=request_meta)
        except TypeError:
            raise DropItem('Missing "image_url" in Response: %s;'
                           % item['referer'])

    def item_completed(self, results, item, info):
        """Success Case"""
        if not results[0]:
            raise DropItem('Item contains no image')
        return item

    def file_path(self, request, response=None, info=None):

        media_ext = os.path.splitext(request.url)[1]

        if request.meta.get('album'):
            return '%s/%s_%s/%s_p%s%s' % (request.meta['user_id'], request.meta['artist_id'], 
                                          request.meta['illust_id'], request.meta['illust_id'], 
                                          request.meta['image_num'], media_ext)

        return '%s/%s_%s%s' % (request.meta['user_id'], request.meta['artist_id'], 
                               request.meta['illust_id'], media_ext)
