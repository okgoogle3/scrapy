import hashlib
import time

from scrapy.utils.project import get_project_settings
import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver

from new_proj.items import NewProjItem


class MySpider(scrapy.Spider):
    name = 'volunteers'
    BASE_URL = "https://suspilne.media/tag/volonteri/"
    LOAD_NEWS_BNT = (By.XPATH, '//a[@class="c-action-link js-load-more-button"]')
    HEAD = (By.XPATH, '//h1')
    ARTICLE_CARDS = (By.XPATH, '//a[@class="c-article-card__headline"]')
    ARTICLE_TITLE_TEXT_XPATH = '//h1/text()'
    ARTICLE_TEXT_XPATH = '//div[@class="c-article-content c-article-content--bordered"]//p/text()'

    def start_requests(self):
        settings = get_project_settings()
        driver_path = settings['CHROME_DRIVER_PATH']
        options = webdriver.ChromeOptions()
        options.headless = True
        driver = webdriver.Chrome(driver_path, options=options)
        driver.get(self.BASE_URL)
        load_news_btn = driver.find_element(self.LOAD_NEWS_BNT[0], self.LOAD_NEWS_BNT[1])
        main_title = driver.find_element(self.HEAD[0], self.HEAD[1])
        actions = ActionChains(driver)
        for i in range(40):
            actions.move_to_element(load_news_btn).perform()
            load_news_btn.click()
            time.sleep(2)
        actions.move_to_element(main_title).perform()
        link_elements = driver.find_elements(self.ARTICLE_CARDS[0], self.ARTICLE_CARDS[1])
        for link_el in link_elements[950:1000]:
            yield Request(link_el.get_attribute("href"), callback=self.parse)

    def parse(self, response):
        item = OurTeamworkItem()
        item['article_uuid'] = hashlib.sha256(str(response.url).encode('utf-8')).hexdigest()
        item['article_title'] = response.xpath(self.ARTICLE_TITLE_TEXT_XPATH).extract()
        item['article_text'] = "\n".join(response.xpath(self.ARTICLE_TEXT_XPATH).extract())
        yield item
