# lead_scraper_orm
Based off my orignal [lead_scraper](https://github.com/pydo/lead_scraper) but now with SQLAlchemy as the ORM.

Tested on python3.4 on ubuntu 14.04 .

It shouldn't be difficult to get working on python2.7 and on Windows.

# Usage
1. Run models.py to create the sqlite database.

        usage: lead_scraper_orm.py -s SEARCHTERM -c CITY -p PROVINCE 
  example:
                  
      lead_scraper_orm.py -s IT -c Toronto -p ON
