from bs4 import BeautifulSoup
import json, os, time, errno, sys
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pyperclip
import sys
sys.setrecursionlimit(11300)

import re
import datetime
import calendar
import ujson
import csv

def mkdir_p(path):
    """
    This is functionally equivalent to the mkdir -p [fname] bash command
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

"""
Page crawling:
Submission table: <div class="table-body submissions-list-wrapper table--striped"></div>
"""
def GetHeaderAttrs(header):
    header = header.split("\n")
    attrs = []
    n = False
    for line in header:
        if n:
            attr = line.replace("<p>", "").replace("</p>", "")
            if attr == "": attr = "ViewLink"
            attrs.append(attr)
            n = False
        elif '<div class=' in line: n = True
    return attrs

def LoadCredentials(loc):
    creds = None
    try:
        with open(loc, "r") as fp:
            creds = json.load(fp)
    except:
        print("Could not load credentials")
        exit(-1)
    return creds


def main():
    settings = None
    creds = None

    grades = {}
    found_subs = False

    assignment_name = None
    scraped = set([])

    # Grab args from command line.
    if len(sys.argv) < 2:
        print("No settings file?")
        exit(-1)
    try:
        with open(sys.argv[1], "r") as fp:
            settings = json.load(fp)
    except:
        print("Could not load given settings file.")
        exit(-1)

    # Get hackerrank credentials:
    creds = LoadCredentials(settings["hackerrank_creditials"])
    # Assignment name
    assignment_name = settings["assignment_name"]
    # Detection workspace
    detection_ws = settings["detection_workspace"]

    # Relevant URLs
    top_level_url = "https://www.hackerrank.com"
    login_url = settings["hackerrank_login_url"]
    submissions_url = settings["hackerrank_submissions_url"]
    contest_url = settings["hackerrank_contest_url"]

    # Where's our headless browser driver?
    driver_path = settings["headless_browser_driver"]

    # Fire up that headless browser.
    driver = webdriver.Firefox(executable_path = driver_path)
    wait = WebDriverWait(driver, 10)

    # Navigate to login page
    driver.get(login_url)
    user = wait.until(EC.visibility_of_element_located((By.ID, "input-1")))
    #  Enter our username
    user.clear()
    user.click()
    user.send_keys(creds["username"])
    #  Enter our password
    # //*[@id="login"]/
    # <input id="password" type="password" name="password" placeholder="Password" data-analytics="AuthPageInput" data-attr1="UserName" data-attr2="Login" data-attr3="master">
    password = driver.find_element_by_xpath('//input[@id="input-2"]')
    password.clear()
    password.click()
    password.send_keys(creds["password"])
    #  Submit!
    # <button class="btn btn-primary login-button auth" name="commit" type="submit" value="request" data-analytics="LoginPassword" data-attr1="master">Log In</button>
    driver.find_element_by_xpath('//button[@type="submit"]').click()
    time.sleep(2) # Sleep some time to let things load before moving on.
    
    
    grades = {}

    # Open contest page
    # Get start date and time
    # Get end date
    # Calculate contest time and save
    driver.get(contest_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    start = str(soup.find("span", {"class":"start-time"})).split('>')[1].split('<')[0]
    start = start.split()
    start_year = int(start[2].strip(','))
    for i in range(1,14):
        if start[0].strip(',') == calendar.month_name[i] or start[0].strip(',') == calendar.month_abbr[i]:
                start_month = i
                break
    else:
        print("Couldn't find start month.")
        exit()
    start_day = int(start[1].strip(','))
    start_hour = 0 if (int(start[3].split(':')[0]) == 12 and start[4] == "am") \
        else (int(start[3].split(':')[0]) + (12 if start[4] == "pm" else 0))
    start_minute = int(start[3].split(':')[1])
    start = datetime.datetime(start_year,start_month,start_day,start_hour,start_minute)

    # This is the old way I grabbed the end time of a contest.
    # It required that "Due: <weekday>, <month> <day>, <year>"
    # was somewhere in the about section of the contest.
    # I have since moved it to the scraper settings json.
    """
    end = soup(text=re.compile("Due:"))[0].split(':')[1].strip()
    end = end.split()
    end_year = int(end[3].strip(','))
    for i in range(1,14):
        if end[1].strip(',') == calendar.month_name[i] or end[1].strip(',') == calendar.month_abbr[i]:
                end_month = i
                break
    else:
        print("Couldn't find end month.")
        exit()
    end_day = int(end[2].strip(','))
    end_hour = 0
    end = datetime.datetime(end_year,end_month,end_day,end_hour)
    """

    # This is the new (arguably better) way of getting end time
    end_year = settings["end_year"]
    end_month = settings["end_month"]
    end_day = settings["end_day"]
    end_hour = 0
    end = datetime.datetime(end_year,end_month,end_day,end_hour)
    end += datetime.timedelta(days=1)

    due_time = (end-start).total_seconds()//60

    # Need to get best submission info for:
    #   Before due date
    #   Each day after up to five days

    i = 1
    while True:
        print("Gathering grades from page %d..." % i)
        driver.get(os.path.join(submissions_url, str(i)))
        time.sleep(2) # Give page time to load.
        # loop through lines in table
        #wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "submissions_list-header")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        #<header class="submissions_list-header">
        header = soup.find("header", {"class": "submissions_list-header"})
        header = GetHeaderAttrs(str(header))
        header = {header[i]:i for i in range(0, len(header))}
        subs = soup.find_all("div", {"class":"judge-submissions-list-view"})
        if len(subs) == 0: break # If there are no submissions on this page, break.
        for sub in subs:
            #['Problem', 'Team', 'ID', 'Language', 'Time', 'Result', 'Score', 'Status', 'During Contest?', 'ViewLink']
            # if not checked: continue
            # - get student name
            # - get problem
            # - get link to code
            link = sub.find("a", {"class": "view-results"})["href"]
            line = sub.find_all("div", {"class": "submissions-title"})
            checked = 'checked=""' in str(line[header["Status"]])
            #if not checked: continue
            problem = line[header["Problem"]].find("a").string
            student = line[header["Team"]].find("a").string
            subtime = line[header["Time"]].find("p").string
            language = line[header["Language"]].find("p").string
            score = line[header["Score"]].find("p").string
            # If we haven't seen this student yet, give them a dictionary.
            if not student in grades: grades[student] = {"problems":{}}
            # If we haven't seen this problem for this student yet, add a list for it.
            if not problem in grades[student]["problems"]: grades[student]["problems"][problem] = [0]
            
            completion_time = int(subtime)
            days_late = int(max(completion_time-due_time,0)//(60*24))
            if days_late > 5: continue
            while days_late >= len(grades[student]["problems"][problem]):
                grades[student]["problems"][problem].append(grades[student]["problems"][problem][-1])
            # If we've already found a solution for this problem from this student:
            float_score = float(score)
            if float_score > grades[student]["problems"][problem][days_late]:
                for index in range(days_late,len(grades[student]["problems"][problem])):
                    if grades[student]["problems"][problem][index] > float_score:
                        break
                    grades[student]["problems"][problem][index] = float_score
            #grades[student]["problems"][problem][days_late] = max(grades[student]["problems"][problem][days_late], float(score))
        i += 1
    with open("grades.json", "w") as f:
        ujson.dump(grades, f)
    #with open("grades.json", "r") as f:
    #   grades = ujson.load(f)
    scores = {}
    extra_credit_identifier = settings["extra_credit_identifier"]
    extra_credit_regular_value = settings["extra_credit_regular_value"]
    for_csv = [["hackerrank_name","scores","best_score",'extra_credit']]
    for student in grades:
        csv_scores = []
        ec_scores = []
        scores[student] = {"scores":[]}
        grades[student]["scores"] = []
        max_late = max([len(grades[student]["problems"][problem]) for problem in grades[student]["problems"]])
        for i in range(max_late):
            score = 0
            for problem in grades[student]["problems"]:
                # extra credit stuff
                if extra_credit_identifier in problem:
                   score += min(extra_credit_regular_value,grades[student]["problems"][problem][i if i < len(grades[student]["problems"][problem]) else -1]) * (1-float(i)/10)
                   ec_scores.append(max(0,grades[student]["problems"][problem][i if i < len(grades[student]["problems"][problem]) else -1]-extra_credit_regular_value) * (1-float(i)/10))
                   continue
                score += grades[student]["problems"][problem][i if i < len(grades[student]["problems"][problem]) else -1] * (1-float(i)/10)
            grades[student]["scores"].append(score)
            scores[student]["scores"].append(score)
            csv_scores.append(score)
        grades[student]["best_score"] = max(grades[student]["scores"])
        scores[student]["best_score"] = max(scores[student]["scores"])
        for_csv.append([student,csv_scores,max(csv_scores),ec_scores])
    #with open("grades.json", "w") as f:
    #    ujson.dump(grades, f)
    with open("scores.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(for_csv)




if __name__ == "__main__":
    main()