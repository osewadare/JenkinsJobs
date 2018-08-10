import jenkins
import datetime
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def get_commit_jobs(url, username, password):
    instance = jenkins.Jenkins(url, username, password)
    jobs = instance.get_jobs()

    # Iterates over jobs getting Job name and last build status and committing to database.
    for job in jobs:
        job_name = job['name']
        build_info = checkbuildstatus(job_name, instance)
        build_status = build_info[0]
        checked = build_info[1]
        commit_jobs(job_name, checked, build_status)
    print('Data committed to database')

# Checks the last build status for a job
def checkbuildstatus(job_name, server):
    build_info = []
    build_status = ''
    job_info = server.get_job_info(job_name)
    last_build = job_info['lastBuild']
    if last_build is None:
        build_status = 'No Build Yet'
    else:
        global last_build_no
        last_build_no = last_build['number']
        global now
        now = datetime.datetime.now()
        last_build_status = server.get_build_info(job_name, last_build_no)['result']
        if last_build_status == 'SUCCESS':
            build_status = 'Success'
        else:
            build_status = 'Failed'
    build_info.append(build_status)
    build_info.append(now)
    return build_info

#Commits the job info to the database
def commit_jobs(job_name, checked, build_status):
    new_job = Job(name=job_name, datetime_checked=checked, status=build_status)
    session.add(new_job)
    session.commit()
    print (job_name)
    print (build_status)
    print (checked)


Base = declarative_base()

# Define the blueprint of the 'Job' table
class Job(Base):
    __tablename__ = 'job'
    #Defines the columns in the 'Job' table
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    datetime_checked = Column(DateTime)
    status = Column(String(15))

#Creates a database engine
engine = create_engine('sqlite:///jenkinsjobs.db')

#Creates table in the engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)

session = DBSession()

url = input ('Jenkins instance URL: ')
username = input('Username: ')
password = input('Password: ')

get_commit_jobs(url, username, password)

