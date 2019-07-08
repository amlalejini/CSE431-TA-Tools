# TA Tools - Spring 2018, Fall 2018, Spring 2019

**TA:** :octocat: [rileyannis](https://github.com/rileyannis)

These scripts were developed for the Spring 2018, Fall 2018, and Spring 2019 semesters of CSE 431 algorithm engineering class at Michigan State University. They are mostly modified versions of those written by [amlalejini](https://github.com/amlalejini) for when he was a TA for the course in [Spring 2017](../2017-spring/). As such, most of the scripts (and this readme) are very similar.

[HackerRank](https://www.hackerrank.com/) competitions were created to mediate homework assignments. The scripts included in this directory were used to scrape student submissions from our HackerRank competitions and check for plagiarism.

Additionally, I wrote a grade scraper that uses the same methodology as (and borrows code heavily from) the code scraper that gathers all of the grades into a csv file. I only wrote this one for Linux, but as I note down below, it should be fairly easy to modify it for your usage.

**DISCLAIMER**: Not very much thought was put into keeping these scripts clean. Once I had them working, I more or less stopped modifying them. As such, they should work, but they may need some minor tweaks. The Windows versions specifically I have not touched since Spring 2018. Feel free to contact me with your specific issue if you're having trouble getting any of the scripts working/doing what you want. I've probably run into the same problem you're having.

## Scraping Solutions

I scraped student solutions in two steps: (1) use a headless browser (controlled by a Python script) to download student submissions and (2) parse out the actual code bit of the student's submission. At the time, there was no API for downloading contest submissions, so be prepared for the disgusting workflow that is described below.

During my time as a TA for CSE 431, I used Windows with Python 2.7 for a semster and Linux with Python 3.6/3.7 for two semesters (obligatory I use Arch btw). Since Alex used primarily MacOS (and Python 2.7), the scripts in this folder are modified from his to run on the above two operating systems/Python versions. Most of the necessary changes are fairly minor and could probably be made to run on your OS/Python version of choice.

When pandas was dumping to a file on Windows, it was exceeding the recursion depth for an unknown reason. As such, I had to extend the recursion limit. [find_recursionlimit.py](http://svn.python.org/projects/python/trunk/Tools/scripts/find_recursionlimit.py) is an official python script you can run to see how high you can increase the depth to. I continued to use this when I moved to Linux.

Relevant scripts:
- Linux/Python3
  - [linuxCodeScraper.py](./scripts/linuxCodeScraper.py)
    - Description
      - This script uses the Selenium web driver to log on to a HackerRank competition, loop over student submissions, and copy submission contents (by ctrl-A, ctrl-C, and ctrl-V'ing into a text file).
    - Dependencies
      - [Selenium](https://www.seleniumhq.org/) - headless browsing
      - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
      - [geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/)
      - [pyperclip](https://pypi.org/project/pyperclip/) - clipboard
    - Usage
      - `python linuxCodeScraper.py settingsfile`
        - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).
        - This script requires hacker rank credentials (provided in a JSON file). An [example credentials file can be found here](./creds/ex_hr_creds.json). No worries, these aren't real credentials. I would only store these locally and under password protection (e.g., require admin privs to access).
  - [linuxPasteExtract.py](./scripts/linuxPasteExtract.py)
    - Description
      - linuxCodeScraper.py outputs .paste files (paste output from student submissions). This script takes that paste output and parses out the actual submission code.
    - Dependencies
      - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
    - Usage
      - `python linuxPasteExtract.py settingsfile`
        - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).
  - [linuxGradeScraper.py](./scripts/linuxGradeScraper.py)
    - Description
      - This script uses the Selenium web driver to log on to a HackerRank competition, loop over student submissions, copy grades into a big json, then create a csv with the final grades. This csv will have rows containing a student's HackerRank name, a list of their scores with the 10% penaly preapplied for each late day that they have submissions (with the 0th indexed score being their score on or before the due date, and the 1st and later being for 1 or more days late up to a maximum of 5), the best score overall assuming they do not use an extension, and a list of their extra credit scores (again with preapplied penalty for each day).
      - It assumes that there is only one problem that provides extra credit. If this problem also provides regular credit towards their actual homework grade, you will set how many points of this problem are **NOT** extra credit in the json settings file, i.e what the standard value of the problem is.
      - Something to note is that if a student uses an extension, their actual best score should be checked for by undoing the penalty on the aforementioned list. This was something I meant to add to the output but didn't get around to. It should be east enough to add this in.
    - Dependencies
      - [Selenium](https://www.seleniumhq.org/) - headless browsing
      - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
      - [geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/)
      - [pyperclip](https://pypi.org/project/pyperclip/) - clipboard
      - [ujson](https://pypi.org/project/ujson/) - writing json files nicely. I don't remember specifically why I used this over the regular json module (I think it related to ease of writing and what I was working on at the time), but I definitely had a reason
    - Usage
      - `python linuxGradeScraper.py settingsfile`
        - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).
- Windows/Python2
  - [winCodeScraper.py](./scripts/winCodeScraper.py)
    - Description
      - This script uses the Selenium web driver to log on to a HackerRank competition, loop over student submissions, and copy submission contents (by ctrl-A, ctrl-C, and ctrl-V'ing into a text file).
    - Dependencies
      - [Selenium](https://www.seleniumhq.org/) - headless browsing
      - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
      - [geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/)
      - [pywin32](https://pypi.org/project/pywin32/) - clipboard
    - Usage
      - `python winCodeScraper.py settingsfile`
        - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).
        - This script requires hacker rank credentials (provided in a JSON file). An [example credentials file can be found here](./creds/ex_hr_creds.json). No worries, these aren't real credentials. I would only store these locally and under password protection (e.g., require admin privs to access).
  - [winPasteExtract.py](./scripts/winPasteExtract.py)
    - Description
      - winCodeScraper.py outputs .paste files (paste output from student submissions). This script takes that paste output and parses out the actual submission code.
    - Dependencies
      - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
    - Usage
      - `python winPasteExtract.py settingsfile`
        - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).

## Plagiarism Detection

I used the [Moss system](https://theory.stanford.edu/~aiken/moss/) for detecting plagiarism. Given a bunch of code files, Moss will analyze the given code, looking for similar code. Moss has some built-in smarts for several languages. I won't get into how to use Moss here. For that, refer to their [website](https://theory.stanford.edu/~aiken/moss/). That said, if you use the same file structure laid out here, the basic usecase that should work for you is `<path to moss> detection_workspace/<Contest Name>/code`.

My workflow:

- First, poke around on the internet for solutions posted on stackoverflow, github, etc. You don't have to be too clever here. Pretend you are a student intending to copy code from the internet, and do the obvious searches. 
- Use both the student submissions and any solutions found online as input to Moss.
- Then comes the tedious bit of combing through high-similarity code comparisons.
