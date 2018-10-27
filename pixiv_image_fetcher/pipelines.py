# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

"""Overload default file pipeline

Only saves jpgs and pngs
"""
import os.path

import scrapy
from scrapy.pipelines.files import FilesPipeline
from scrapy.exceptions import DropItem

class PixivImagePipeline(FilesPipeline):

    def get_media_requests(self, item, info):
        """Overriden for Exception Handling"""
        try:
            if 'image_num' not in item:
                image_num = None
            else:
                image_num = item['image_num'][0]

            return scrapy.Request(item['image_urls'][0], 
                                  headers={
                                      'referer': item['referer'][0]
                                  },
                                  meta={
                                      'user_id' : item['user_id'][0],
                                      'artist_id' : item['artist_id'][0],
                                      'illust_id' : item['illust_id'][0],
                                      'image_num' : image_num,
                                  })
        except TypeError:
            raise DropItem('Missing "image_url" in Response: %s;'
                           % item['referer'][0])
        except ValueError:
            raise DropItem('Image is an album')

    def item_completed(self, results, item, info):
        """Success Case"""
        if not results[0]:
            raise DropItem('Item contains no image')

        print('Image from %s downloaded!' % item['image_urls'][0])
        return item

    def file_path(self, request, response=None, info=None):

        media_ext = os.path.splitext(request.url)[1]

        if request.meta['image_num']:
            return '%s/%s_%s/%s_%s%s' % (request.meta['user_id'], request.meta['artist_id'], 
                                         request.meta['illust_id'], request.meta['illust_id'], 
                                         request.meta['image_num'], media_ext)

        return '%s/%s_%s%s' % (request.meta['user_id'], request.meta['artist_id'], 
                               request.meta['illust_id'], media_ext)
