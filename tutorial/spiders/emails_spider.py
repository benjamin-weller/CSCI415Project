import scrapy
import csv
from bs4 import BeautifulSoup
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


def write_email_output(email, url):
    myData = []
    #Check to see if it's a duplicate
    with open('trial.csv', 'w') as myFile:
        writer = csv.writer(myFile)
        myData.append([email, url])
        writer.writerows(myData)

def check_csv_for_duplicates(email, path):
    trial_list = []
    with open(path, 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            trial_list.append(row[0])
        trial_set = set(trial_list)
        trial_set.add(email)
        trial_set_length = len(trial_set)
        return not trial_set_length == len(trial_list) #If the element is new this will return true, if it's a copy it'll return false

class EmailsSpider(CrawlSpider):
    name = "Emails"
    depth = 100
    path = None;
    urls = []

    rules = [Rule(LinkExtractor(), follow=True, callback="parse_emails")]

    def start_requests(self):
        self.path = input("Please pass the path of the .csv file that contains your URLs: ")
        with open(self.path, 'r') as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                for entry in row:
                    if entry:
                        self.urls.append(entry)
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_emails)




    def parse_emails(self, response):
        self.depth -=1
        # If we've exceeded our depth limited search, then return.
        if self.depth<0:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        anchor_list = soup.find_all("a")

        # Little bit of defensive programming here, what if there are not links on the page??
        if not anchor_list:
            return

        for tag in anchor_list:
            if "href" in tag.attrs.keys(): #Grabs the atrributes of that tag as a dictionary
                result = re.search(r"mailto:", tag["href"])
                if result:
                    # Prepare the email to be written to the CSV
                    email = tag["href"][result.end():]
                    # print("Our email is ",email)
                    write_email_output(email, response.url)
                    # print("We have found "+str(email)+" on the page with URL, "+str(response.url))

        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
