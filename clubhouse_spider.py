import scrapy
import pandas as pd
import csv
from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
import re
from selenium.webdriver.chrome.options import Options

class TspSpider(scrapy.Spider):
    name = 'clubhouse_spider'

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = Chrome(options=chrome_options)

    def __init__(self, input_file='', **kwargs):
        self.input_file_name = input_file

    def start_requests(self):
        # df = pd.read_csv(self.input_file_name)
        # for i in range(0,len(df)):
        #     data = df.loc[[i]].to_dict()
        #     url = df.loc[i,'url']
        #     if(str(url) == 'nan'):
        #         username = list(data['photo_url'].values())[0]
        #         if(str(username) != 'nan'):
        #             url = 'https://www.clubhousedb.com/user/' + username
        #     if('/user/' in url):
        #         yield scrapy.Request(url=url, callback=self.parse_data)
        
        yield scrapy.Request(url="https://clubhousedb.com/user/christine", callback=self.parse_data)

    def parse_data(self, response):
        f = dict()
        f['username'] = response.xpath("//div[contains(@class,'username')]/span[1]/text()").get()
        f['image'] = response.xpath("//div[@class='img-col']/img/@src").get()
        f['desc'] = "\n".join(response.xpath("//section[@class='user-bio']/p//text()").getall())
        if('[email\xa0protected]' in f['desc']):
            self.driver.get(response.request.url)
            desc = self.driver.find_elements_by_xpath("//section[@class='user-bio']/p")
            if(desc):
                desc_text =desc[0].text
            else: 
                desc = ''
            match_objects = re.findall(r'\w+@\w+[\.\w+]+', desc_text)
            email = ", ".join(match_objects)
            f['desc'] = desc_text
            f['email'] = email
        else:
            f['email'] = ''
        f['insta'] = "".join(response.xpath("//*[name()='use' and @*='#instagram']/ancestor::span[1]/text()").getall())
        f['twitter'] = "".join(response.xpath("//*[name()='use' and @*='#twitter']/ancestor::span[1]/text()").getall())
        f['ref'] = response.xpath("//p[contains(text(),'Invited by: ')]/a/text()").get()
        f['ref_link'] = response.xpath("//p[contains(text(),'Invited by: ')]/a/@href").get()
        users = response.xpath("//section[@class='user-clubs']/div/div/a")
        f['members_of'] = [{'club_name':''.join(x.xpath('./text()').getall()).strip(), 'club_link': x.xpath("./@href").get(),'club_picture': x.xpath("./div/img/@src").get()} for x in users]

        for k,v in f.items():
            if(v != None):
                try:
                    f[k] = v.strip()
                except:
                    pass


        yield f
