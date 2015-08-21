import time
import requests
from lxml import html
from lxml.html.clean import Cleaner
import datetime
import argparse

from models import Job, session


class Indeed:
    """indeed.ca scraper. Takes in url parameter including search terms and location that
    will be fed into the url"""

    def __init__(self, args):
        self.searchterm = args.searchterm
        self.city = args.city
        self.province = args.province

    def crawl(self):
        # count starts at first page
        crawling = True
        count = 0
        while crawling:
            # time.sleep(5)
            searchterm = self.searchterm
            city = self.city
            prov = self.province
            url = "http://ca.indeed.com/jobs?q={0}&l=+{1}+%2C{2}&start={3}".format(searchterm, city, prov, str(count))
            print(url, 'current URL')
            page = requests.get(url)
            tree = html.fromstring(page.text)
            # cleans html by removing <b></b> tags in the description
            # These tags caused a bug where the descriptions were fragmented on multiple rows
            cleaner = Cleaner()
            cleaner.remove_tags = ['b']
            tree = cleaner.clean_html(tree)
            jobtitles = tree.xpath('//h2[@class="jobtitle"]/a/text()')
            joblinks = tree.xpath('//h2[@class="jobtitle"]/a/@href')
            job_descriptions = tree.xpath('//span[@class="summary"]/text()')
            job_location = tree.xpath('//span[@class="location"]/span/text()')
            company = tree.xpath('//span[@class="company"]/text()')
            job_posted_date = tree.xpath('//span[@class="date"]/text()')
            job_posted_date = (job.lstrip() for job in job_posted_date)
            company = (job.lstrip() for job in company)
            job_location = (job.lstrip() for job in job_location)
            jobtitles = (job.lstrip() for job in jobtitles)
            joblinks = (job.lstrip() for job in joblinks)
            job_descriptions = (job for job in job_descriptions)
            for _ in jobtitles:
                Database.add_entry(jobtitles=next(jobtitles),
                                   joblinks=next(joblinks),
                                   job_descriptions=next(job_descriptions),
                                   job_location=next(job_location),
                                   company=next(company),
                                   job_posted_date=next(job_posted_date))
            link_pages = tree.xpath('//div[@class="pagination"]/a/@href')
            print(link_pages, 'link_pages')
            # look for next button
            # if no longer present it means we have reached the last page
            next_button = tree.xpath('//*[@id="resultsCol"]/div/a/span/span/text()')
            next_button_str = ''.join(next_button)
            print(next_button)

            if u'Next' in next_button_str:
                print('found next will continue scraping...')
            else:
                print('Hit last page, crawler will stop...')
                crawling = False

            for page in link_pages:
                # takes digits from end of url
                # takes last 6 characters, unlikely that the number would be any bigger
                p = page[-6:]
                digits_url = ''.join([d for d in p if d.isdigit()])
                try:
                    print(digits_url, 'digits url')
                    if int(digits_url) > count:
                        print(page, 'page')
                        count = int(digits_url)
                        print(count, 'count')
                    else:
                        print('You probably broke your conditional statement...')
                        print(digits_url, 'current count {}'.format(count))
                except ValueError:
                    # print("We're on the first page so no int in the page url")
                    print('This failed', digits_url)


class Database:
    @staticmethod
    def add_entry(jobtitles, joblinks, job_descriptions, job_location, company, job_posted_date):

        job = Job(job_title=jobtitles,
                  job_link=joblinks,
                  job_description=job_descriptions,
                  job_location=job_location,
                  company=company,
                  job_posted_date=job_posted_date,
                  crawl_timestamp=datetime.datetime.now())
        s = session()
        s.add(job)
        # s.add_all(job)
        s.commit()


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape indeed.ca and save results to sqlite database')
    parser.add_argument("-s", "--searchterm", action="store",
                        help="specify a search query", required=True)
    parser.add_argument('-c', '--city', action='store',
                        help='specify a city for the search query', required=True)
    parser.add_argument('-p', '--province', action='store',
                        help='specify a province for the search query', required=True)

    return parser.parse_args()


if __name__ == '__main__':
    search = Indeed(parse_args())
    search.crawl()