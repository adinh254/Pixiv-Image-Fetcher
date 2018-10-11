import scrapy

class BaseSpider(scrapy.Spider):
    name = "login"
    start_urls = ["https://accounts.pixiv.net/login"]

    # Attempt to login
    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata = {"pixiv_id" : "lazeegutar@gmail.com", "password" : "2aseChuW"},
            callback = self.after_login
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
        return Request(url = "https://www.pixiv.net/bookmark.php", 
            callback = self.parse_bookmarks)
    
    # Points to each bookmarked image
    # Call ExtractionSpider
    def parseBookmarks(self, response):
        # Selector Variable

        # Loop response body and check select variable

        
    