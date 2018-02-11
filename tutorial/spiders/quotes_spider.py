import scrapy
import csv

class QuotesSpider(scrapy.Spider):
    name = "Emails"

    def start_requests(self):
        urls =[]
        path = input("Please pass the path of the .csv file that contains your URLs: ")
        with open(path, 'rb') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                urls.append(row.split(','))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)