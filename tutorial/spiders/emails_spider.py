import scrapy
import csv
from bs4 import BeautifulSoup
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


def write_email_output(email, url):
    myData = []
    #Check to see if it's a duplicate
    with open('output.csv', 'w+') as myFile:
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

def get_initial_urls():
    urls = []
    # path = input("Please pass the path of the .csv file that contains your URLs: ")
    path = "C:\\Users\\Owner\\Documents\\Projects\\CSCI415Project\\tutorial\\trial.csv"
    with open(path, 'r') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            for entry in row:
                if entry:
                    urls.append(entry)
    return urls


def capture_domains(list_of_urls):
    returned = []
    for x in list_of_urls:
        regular_expression_search_result = re.search(r"https://|http://", x)
        if regular_expression_search_result:
            returned.append(x[regular_expression_search_result.end():])
    return returned



class EmailsSpider(CrawlSpider):
    name = "Emails"
    path = None;
    urls = get_initial_urls()
    allowed_domains = capture_domains(urls)
    # print(allowed_domains)
    custom_settings = {
        'DEPTH_LIMIT': '3',
    }


    rules = [Rule(LinkExtractor(allow=allowed_domains, unique=True), callback="parse_emails")]

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse_emails)




    def parse_emails(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        anchor_list = soup.find_all("a")

        # Little bit of defensive programming here, what if there are not links on the page??
        if not anchor_list:
            return
        returned = []
        for tag in anchor_list:
            print (f"We are in {response.url}")
            if "href" in tag.attrs.keys(): #Grabs the atrributes of that tag as a dictionary
                email_result = re.search(r"mailto:", tag["href"])
                sanity_result = re.search(r"http://|https://", tag["href"])
                if email_result:
                    # Prepare the email to be written to the CSV
                    email = tag["href"][email_result.end():]
                    # write_email_output(email, response.url)
                    print(f"We would write: {email}, {response.url}")
                elif sanity_result:
                    value = tag["href"]
                    print(f"The URL we will append is: {value}")
                    returned.append(scrapy.Request(url=tag["href"], callback=self.parse_emails))
        return returned
