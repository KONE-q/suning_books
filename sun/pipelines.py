# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SunPipeline(object):
    def process_item(self, item, spider):
        with open('D:/suning/sun/4.txt','a+',encoding='utf-8') as f:
            f.write(str(item['category'])+' '+str(item['shop_name'])+' '+str(item['content'])+' '+str(item['main_href'])+' '+str(item['money'])+' '+str(item['comment'])+'\n')
        return item
