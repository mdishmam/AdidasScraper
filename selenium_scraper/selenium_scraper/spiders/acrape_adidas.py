import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import ActionChains
import time
from selenium.webdriver.common.by import By
from scrapy.http import Request


class AcrapeAdidasSpider(scrapy.Spider):
    name = "scrape_adidas"
    allowed_domains = ["shop.adidas.jp"]
    start_urls = ["https://shop.adidas.jp/item/?gender=mens&order=1"]

    def start_requests(self):
        url = "https://shop.adidas.jp/item/?gender=mens&order=1"
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        driver = response.request.meta["driver"]
        # scroll to the end of the page 10 times
        for x in range(0, 120):
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # time.sleep(2)  # Wait for page to load
            # scroll down by 10000 pixels
            ActionChains(driver) \
                .scroll_by_amount(0, 500) \
                .perform()

            # waiting 2 seconds for the products to load
            time.sleep(1)

        # select all product elements and iterate over them
        for product in driver.find_elements(By.CSS_SELECTOR, "div.itemCardArea-cards.test-card.css-dhpxhu"):
            # scrape the desired data from each product
            url = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            # image = product.find_element(By.CSS_SELECTOR, ".card-img-top").get_attribute("src")
            name = product.find_element(By.CSS_SELECTOR, "div.articleDisplayCard-Title").text
            # price = product.find_element(By.CSS_SELECTOR, "h5").text

            # add the data to the list of scraped items
            # yield {
            #     "url": url,
            #     "name": name,
            # }
            yield Request(response.urljoin(url), callback=self.parse_product)

    def parse_product(self, response):
        image_links = ', '.join(['https://shop.adidas.jp'+i.css('img::attr(src)').get() for i in response.css('div.article_image')])
        bread_crumb = " / ".join([i.css('a::text').get() for i in response.css('li.breadcrumbListItem')[1:]])
        category = response.css('span.genderName.test-genderName::text').get() + " " + response.css('span.categoryName.test-categoryName::text').get()
        name = response.css('h1.itemTitle.test-itemTitle::text').get()
        price = response.css('span.price-value.test-price-value::text').get()
        size_available = ", ".join([i.css('::text').get() for i in response.css('button.sizeSelectorListItemButton')])
        title_of_description = response.css('h4.heading.itemFeature.test-commentItem-subheading::text').get()
        general_description = response.css('div.commentItem-mainText.test-commentItem-mainText::text').get()
        general_description_itemized = ', '.join(i.css('::text').get() for i in response.css('li.articleFeaturesItem.test-feature'))
        # todo: tale of size [size description table]
        rating = response.css('span.BVRRNumber.BVRRRatingNumber::text').get()

        yield {
            'URL': response.url,
            'Name': name,
            'Price': price,
            'Bread Crumbs': bread_crumb,
            'Category': category,
            'Images': image_links,
            'Sizes Available': size_available,
        }


