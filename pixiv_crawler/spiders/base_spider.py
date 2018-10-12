import scrapy

class BaseSpider(scrapy.Spider):
    name = "login"
    start_urls = ["https://accounts.pixiv.net/login"]

    # Attempt to login
    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {"pixiv_id" : "lazeegutar@gmail.com", "password" : "2aseChuW"},
            callback = self.afterLogin
        )
    
    # Case to check login validity
    # Redirect to bookmarks
    def afterLogin(self, response):
        # Login Case
        if b"error-msg-list__item" in response.body:
            self.logger.error("Login failed")
            return
        
        # Generate response
        self.logger.info("Login Successful!")
        return scrapy.Request(url = "https://www.pixiv.net/bookmark.php", 
            callback = self.parseBookmarks)
    
    # Get list of all bookmarked image urls in current page
    # Iterate through list and extract images
    def parseBookmarks(self, response):
        image_urls = response.xpath('//div[@class="display_editable_works"]').css('a.work::attr(href)').extract()

        
