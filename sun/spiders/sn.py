# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import re
import requests

class SnSpider(scrapy.Spider):
    name = 'sn'
    allowed_domains = ['suning.com']
    start_urls = ['http://book.suning.com/']

    def parse(self, response):
        item1 = {}
        item1['book_category'] = response.xpath('//div[@class="menu-list"]/div[@class="menu-item"]/dl/dd/a/text()').extract()#在主页中获得分类的名称
        item1['book_list'] = response.xpath('//div[@class="menu-list"]/div[@class="menu-item"]/dl/dd/a/@href').extract()#获得所有分类的url
        item = {}
        for i in range(0,len(item1['book_category'])):
            item['category'] = item1['book_category'][i]
            item['book_href'] = item1['book_list'][i]
            # print(item)
            num = {}
            num['page'] = 0                                #由于下一页的url获取比较难，通过传递一个参数方便构造url
            yield scrapy.Request(url=item['book_href'],    #通过获取到的url爬取
                callback=self.book_parse,
                meta={'item':deepcopy(item),'num':num}    #为了防止传递的数据被覆盖，通过deepcopy将获取数据后传递
            )



    def book_parse(self,response):
        item = response.meta['item']     #获得传入的数据
        num = response.meta['num']
        # print(item)
        book_list = response.xpath('//div[@class="search-results clearfix mt10"]/div[@class="results-rblock ml10 results-search-list"]/div[@id="filter-results"]/ul/li')
        #获得该页面中所有书本的li
        for i in book_list:
            #获得书店的名称
            item['shop_name'] = i.xpath('./div[@class="border-out"]/div[@class="border-in"]/div[@class="wrap"]/div[@class="res-info"]/p[@class="seller oh no-more "]/a/text()').extract()
            # print(item['shop_name'])
            #获得书本的信息
            index1 = i.xpath('./div[@class="border-out"]/div[@class="border-in"]/div[@class="wrap"]/div[@class="res-info"]/p[@class="sell-point"]/a')
            book_content = index1.xpath('string(.)').extract()
            # print(book_content)
            item['content'] = re.sub('\n',' ',book_content[0]).strip()
            #获得该书本的url
            href = i.xpath('./div[@class="border-out"]/div[@class="border-in"]/div[@class="wrap"]/div[@class="res-info"]/p[@class="sell-point"]/a/@href').extract()
            item['main_href'] = 'http:' + href[0]   #构造url
            # print(main_href)
            yield scrapy.Request(
                item['main_href'],
                callback=self.main_book_parse,
                meta={'item':deepcopy(item)}
            )
        #     # break
        #     print('done----------------------------------------------')

        cur_page = response.xpath('//a[@class="cur"]/@href').extract()  #获取当前页的url ，因为测试的过程中在跳转页面时获取的当前页都是第一次进入的url
        all_page = response.xpath('//span[@class="page-more"]/text()').extract() #获得总的页数
        # print(cur_page)
        num['page'] = num['page'] + 1                             #将转递过来的数据进行修改
        print(num['page'])
        pag = re.compile('\.html').findall(cur_page[0])           #通过正则匹配出符合条件的url
        all_page_num = int(re.compile('共(.*?)页').findall(all_page[0])[0])  #获得总的页数
        print('总页数：'+str(all_page_num))
        # print(type(num['page']),type(all_page_num))
        if num['page'] <= all_page_num:                          #判断url是否超出总的展示页数
            if len(pag) != 0  :                                   #判断获得的url是否符合所需要的
                # print(cur_page)
                a = cur_page[0].split('-')                         #将获得的url进行拆分
                next_page = 'http://list.suning.com'+a[0]
                for i in range(1,len(a)):                         #对下页的url进行构造
                    if i == 2:
                        next_page = next_page +'-'+ str(num['page'])  #由于url中的第三个参数时跳转到下一页的关键。这里通过每一次的callback所传递的num['page']进行修改
                    else:
                        next_page = next_page +'-'+a[i]
                print(next_page)
                yield scrapy.Request(next_page,callback=self.book_parse,meta={'num':deepcopy(num),'item':deepcopy(item)})   #为了防止传递的数据被覆盖，通过deepcopy将获取数据后传递
        else:
            return 0



    def main_book_parse(self,response):
        item = response.meta['item']
        # print(response.url)
        #获得书籍的价格，售出价格好像是通过JavaScript之后得到，不会，所以只能获取书籍的原价
        item['money'] = re.findall('"itemPrice":"(.+)",',response.text)[0]
        good_reputation = response.xpath('//div[@id="appraise"]/a[@target="_blank"]/@href').extract()  #获得评论中所需要的参数
        # print(good_reputation)
        a=re.compile('general-(.+)-1-total.htm').findall(good_reputation[0])   #通过正则提取所需参数
        # print(a)
        #评论数据的url
        commnet_href = 'https://review.suning.com/ajax/cluster_review_lists/general--%s-total-%s-default-10-----reviewList.htm?callback=reviewList'
        comment_list=[]
        for i in range(1,100):
            comment_url = commnet_href%(a[0],i)    #构造评论数据的url，第一个字符串为商品的标识，第二个字符串为评论的页码
            cont = requests.get(comment_url).content.decode()
            content=re.compile('"content":"(.*?)"').findall(cont)  #通过正则获得评论数据
            print('评论数:'+ str(len(content)))
            comment_list.append(content)
            if len(content) < 10:                     #判断评论数据的长度，如果不足就退出循环
                break
        item['comment'] = comment_list
        return item