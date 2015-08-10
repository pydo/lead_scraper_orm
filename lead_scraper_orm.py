import time
import requests
from lxml import html
from lxml.html.clean import Cleaner

from models import Job, session


class Indeed:
    """indeed.ca scraper. Takes in url parameter including search terms and location that
    will be fed into the url"""

    def __init__(self, searchterm, city, province):
        self.searchterm = searchterm
        self.city = city
        self.province = province

    def crawl(self):
        # count starts at first page
        crawling = True
        count = 0
        time.sleep(5)
        while crawling:
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
            jobtitles = (job.lstrip() for job in jobtitles)
            joblinks = (job.lstrip() for job in joblinks)
            job_descriptions = (job for job in job_descriptions)
            Database.add_entry(zip(jobtitles, joblinks, job_descriptions))
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
                    if digits_url > count:
                        print(page, 'page')
                        count = int(digits_url)
                        print(count, 'count')
                    else:
                        print('You probably broke your conditional statement...')
                        print(digits_url, 'current count {}'.format(count))
                except ValueError:
                    # print("We're on the first page so no int in the page url")
                    print('This failed', digits_url)


class Database(object):
    @staticmethod
    def add_entry(job_offers):
        job = Job(job_offers)
        s = session()
        s.add(job)
        s.commit()


def main():
    """Run test object first to scrape and populatre SQL DB
    then run Database.filter_jobs to find what you're looking for

    ex: Indeed(job, city, province/state)
    """
    test = Indeed('manager', 'Toronto', 'ON')
    test.crawl()
    # search_terms = Database.filter_jobs('trainsim')
    # search_terms = Database.filter_jobs
    # send_mail('recipient@email.com', search_terms('manager'))


if __name__ == '__main__':
    main()