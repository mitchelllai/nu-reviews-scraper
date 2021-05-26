from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from dotenv import load_dotenv
import os

BASE_URL = 'https://class-descriptions.northwestern.edu/'

# REFACTOR SCRIPT BELOW:
# def get_elements(driver, url):
#     driver.get(url)
#     content = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
#     len_content = len(content)
#     for i in range(len_content):
#         values = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
#         value = values[i].text
#         print(value)

load_dotenv()
DB_HOST = os.environ['DB_HOST']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_NAME = os.environ['DB_NAME']
client = MongoClient("mongodb+srv://"+DB_USERNAME+":"+DB_PASSWORD+"@"+DB_HOST+"/"+DB_NAME+"?retryWrites=true&w=majority")
db = client['nu-reviews']

# FOR TESTING IN ORDER TO CLEAR ALL DOCUMENTS IN DB
toggle_clear = False

if toggle_clear:
    db['courses'].delete_many({})
    db['profs'].delete_many({})
else:
    options = Options()
    options.headless = True
    driver = Chrome(chrome_options=options)
    driver.get(BASE_URL)
    content = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
    len_content = len(content)
    courses = []
    for i in range(len_content):
        terms = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
        term = terms[i].text
        if term == '2021 Summer':
            continue
        # print(term) #Specific quarter that a course is offered
        term_link = terms[i].get_attribute('href')
        driver.get(term_link)
        schools = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
        len_schools = len(schools)
        for j in range(len_schools):
            schools = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
            a_school = schools[j].text
            # print(a_school) #The school that offers the course (e.g., Weinberg, McCormick, etc.)
            school_link = schools[j].get_attribute('href')
            if school_link == BASE_URL or a_school == 'Freshman Seminars':
                continue
            driver.get(school_link)
            subjects = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
            len_subjects = len(subjects)
            for k in range(len_subjects):
                subjects = driver.find_element_by_class_name('content').find_elements(By.TAG_NAME, 'a')
                a_subject = subjects[k].text
                # print(a_subject) #The subject that the course is categorized under
                subject_link = subjects[k].get_attribute('href')
                if a_subject == 'HOME' or a_subject == term.upper():
                    continue
                driver.get(subject_link)
                courses = driver.find_elements_by_css_selector('.expander li')
                len_courses = len(courses)
                for l in range(len_courses):
                    courses = driver.find_elements_by_css_selector('.expander li')
                    courses_expanded = courses[l].find_elements(By.TAG_NAME, 'a')
                    len_courses_expanded = len(courses_expanded)
                    for m in range(len_courses_expanded):
                        courses_expanded = courses[l].find_elements(By.TAG_NAME, 'a')
                        a_course_link = courses_expanded[m].get_attribute('href')
                        driver.get(a_course_link)
                        course_name = driver.find_element_by_css_selector('.content h1').text
                        instructor = driver.find_element_by_css_selector('.content p').text.splitlines()[0]
                        # print(course_name) #name of course
                        # print(instructor) #name of instructor
                        
                        prof = db['profs'].find_one_and_update(
                            {'name' : instructor},
                            {'$addToSet' : {
                                'courses' : course_name,
                                'departments' : a_subject,
                                'schools' : a_school
                                }})
                        if not prof:
                            #Professor object to be entered into db['profs']
                            prof_object = {
                                'name' : instructor,
                                'courses' : [course_name],
                                'departments' : [a_subject],
                                'schools' : [a_school],
                                'scores' : {
                                    'communication' : None,
                                    'engagement' : None,
                                    'fairness' : None,
                                    'helpfulness' : None
                                }
                            }
                            db['profs'].insert_one(prof_object)

                        #Course object to be entered into db['courses']
                        course_object = {
                            'quarter' : term,
                            'school' : a_school,
                            'subject' : a_subject,
                            'course_name' : course_name,
                            'instructor' : instructor,
                            'scores' : {
                                'lectures' : None,
                                'assignments' : None,
                                'difficulty' : None,
                                'time' : None
                            }
                        }
                        db['courses'].insert_one(course_object)
                        print(course_object)

                        driver.back()
                driver.back()
            driver.back()
        driver.back()
    driver.close()