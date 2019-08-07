# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SunItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    # book_href = scrapy.Field()
    shop_name = scrapy.Field()
    content = scrapy.Field()
    main_href = scrapy.Field()
    money = scrapy.Field()
    comment = scrapy.Field()

