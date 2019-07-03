from bs4 import BeautifulSoup
import json, os, time, errno, sys
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
#from appkit import *
import pyperclip
import sys
sys.setrecursionlimit(11300)

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

    student_subs = {}
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

    # Where's our headless browser driver?
    driver_path = settings["headless_browser_driver"]

    # Is there a save file to load?
    savefile_name = os.path.join(detection_ws, assignment_name, settings["pickle"])
    save_data = {}
    if (os.path.isfile(savefile_name)):
        print("Found savefile, loading")
        with open(savefile_name, "rb") as fp:
            save_data = pickle.load(fp)
        found_subs = True
    else:
        print("Did not find savefile, proceeding.")
        found_subs = False

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
    
    # import re
    # import datetime
    # import calendar
    # grades = {}
    # contest_page = "https://www.hackerrank.com/cse-431-spring-2019-assignment-1"

    # # Open contest page
    # # Get start date and time
    # # Get end date
    # # Calculate contest time and save
    # driver.get(contest_page)
    # soup = BeautifulSoup(driver.page_source, "html.parser")
    # start = str(soup.find("span", {"class":"start-time"})).split('>')[1].split('<')[0]
    # start = start.split()
    # start_year = int(start[2].strip(','))
    # for i in range(1,14):
    #     if start[0].strip(',') == calendar.month_name[i] or start[0].strip(',') == calendar.month_abbr[i]:
    #             start_month = i
    #             break
    # else:
    #     print("Couldn't find start month.")
    #     exit()
    # start_date = int(start[1].strip(','))
    # start_time = int(start[3].split(':')[0]) + 12
    # start = datetime.datetime(start_year,start_month,start_date,start_time)

    # end = soup(text=re.compile("Due:"))[0].split(':')[1].strip()
    # end = end.split()
    # end_year = int(end[3].strip(','))
    # for i in range(1,14):
    #     if end[1].strip(',') == calendar.month_name[i] or end[1].strip(',') == calendar.month_abbr[i]:
    #             end_month = i
    #             break
    # else:
    #     print("Couldn't find end month.")
    #     exit()
    # end_date = int(end[2].strip(','))
    # end_time = 0
    # end = datetime.datetime(end_year,end_month,end_date,end_time)
    # end += datetime.timedelta(days=1)

    # due_time = end-start).total_seconds()//60
    # day_late_1 = due_time + 60*24
    # day_late_2 = day_late_1 + 60*24
    # day_late_3 = day_late_2 + 60*24
    # day_late_4 = day_late_3 + 60*24
    # day_late_5 = day_late_4 + 60*24

    # # Need to get best submission info for:
    # #   Before due date
    # #   Each day after up to five days

    # exit()

    # Start getting code
    if found_subs:
        student_subs = save_data["student_subs"]
    else:
        i = 1
        while True:
            print("Scraping page %d..." % i)
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
                if not student in student_subs: student_subs[student] = {}
                # If we haven't seen this problem for this student yet, add a dictionary for it.
                if not problem in student_subs[student]: student_subs[student][problem] = {}

                # If we've already found a solution for this problem from this student:
                if "time" in student_subs[student][problem]:
                    # Take only if higher score.
                    if float(student_subs[student][problem]["score"]) >= float(score):
                        continue
                    if float(student_subs[student][problem]["time"]) < float(subtime):
                        continue
                # Take unconditionally
                student_subs[student][problem]["link"] = link
                student_subs[student][problem]["time"] = subtime
                student_subs[student][problem]["language"] = language
                student_subs[student][problem]["score"] = score

            i += 1

        save_data["student_subs"] = student_subs
        # Write out save data.
        with open(savefile_name, "wb") as fp:
            pickle.dump(save_data, fp)

    # Student subs now has all information to go in and download things.
    total_students = len(student_subs)
    cnt = 0
    for student in student_subs:
        print("Student: %s" % student)
        print("  Progress: " + str(cnt + 1) + "/" + str(total_students))
        # Make a home for this student's code scapings.
        student_dir = os.path.join(detection_ws, assignment_name, "scrapings", student)
        mkdir_p(student_dir)
        student_metadata = {"username": student, "submissions": student_subs[student]}
        # For each problem this student submitted...
        for problem in student_subs[student]:
            print("\tProblem: %s" % problem)
            # There's already a solution in the code directory, skip.
            if (os.path.isfile(os.path.join(student_dir, "%s.paste" % problem))):
                print("\t  Already have that, continuing.")
                continue
            # student_metadata["submissions"][problem] = {}
            # student_metadata["submissions"][problem]["link"] = student_subs[student][problem]["link"]
            # student_metadata["submissions"][problem]["language"] = student_subs[student][problem]["language"]
            # student_metadata["submissions"][problem]["score"] = student_subs[student][problem]["score"]
            # student_metadata["submissions"][problem]["time"] = student_subs[student][problem]["time"]
            # Navigate to page with code.
            link = os.path.join(top_level_url, student_subs[student][problem]["link"])
            driver.get(link)
            time.sleep(2)   # Sleep to give time for page to load.
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.1) # Sleep to give time to do command.
            ActionChains(driver).key_down(Keys.CONTROL).send_keys('c').key_up(Keys.CONTROL).perform()
            time.sleep(0.1) # Sleep to give time to do command.
            # Get the clipboard.
            #pb = NSPasteboard.generalPasteboard()
            #pbstring = pb.stringForType_(NSStringPboardType)
            pbstring = pyperclip.paste()
            # Save out code.
            with open(os.path.join(student_dir, "%s.paste" % problem), "wb") as fp:
                fp.write(pbstring.encode('utf-8'))
        # Write out metadata as json file.
        with open(os.path.join(student_dir, "student_metadata.json"), "w") as fp:
            json.dump(student_metadata, fp)
        cnt += 1

if __name__ == "__main__":
    main()
