from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Job(Base):
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    job_title = Column(String)
    job_description = Column(String)
    job_link = Column(String)
    job_location = Column(String)
    job_posted_date = Column(String)
    company = Column(String)
    crawl_timestamp = Column(String)

    def __init__(self, job_title='a', job_description='a', job_link='a', job_location='a', job_posted_date='a', company='a', crawl_timestamp='a'):
        self.job_title = job_title
        self.job_description = job_description
        self.job_link = job_link
        self.job_location = job_location
        self.job_posted_date = job_posted_date
        self.company = company
        self. crawl_timestamp = crawl_timestamp

    def __repr__(self):
        return '<Job %d>' % self.id


engine = create_engine('sqlite:///jobs.sqlite')
session = sessionmaker()
session.configure(bind=engine)
Base.metadata.create_all(engine)
