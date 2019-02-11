# TA Tools - Spring 2017

**TA:** :octocat: [amlalejini](https://github.com/amlalejini)

These scripts were developed for the Spring 2017 CSE 491 (now CSE 431) algorithm
engineering class at Michigan State University.

That semester, we used [HackerRank](https://www.hackerrank.com/) competitions to
mediate homework assignments. The scripts included in this directory were used to
scrape student submissions from our HackerRank competitions.

**DISCLAIMER**: All of these scripts were developed in haste, with little thought
for future proofing, other users (including me), _et cetera_. **I have no idea
if these scripts still work.**

All python scripts were written using Python 2.7 (I had yet to make the switch
over to 3.6).

## Scraping Solutions

I scraped student solutions in two steps: (1) use a headless browser (controlled
by a Python script) to download student submissions and (2) parse out the actual
code bit of the student's submission. At the time, there was no API for downloading
contest submissions, so be prepared for the disgusting workflow that is described
below.

Also, I did the scraping on my Mac laptop, so some of the functionality of these
scripts is Mac-specific. I have no reason to believe that all of the Mac-specific
junk can't be converted to non-Mac-specific junk.

Relevant scripts:

- [codeScraper.py](./scripts/codeScrapper.py)
  - Description
    - This script uses the Selenium web driver to log on to a HackerRank competition,
      loop over student submissions, and copy submission contents (by ctrl-A, ctrl-C,
      and ctrl-V'ing into a text file).
  - Dependencies
    - [Selenium](https://www.seleniumhq.org/) - headless browsing
    - [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - html parsing
    - AppKit - Accessing copy clipboard
    - [geckodriver](https://firefox-source-docs.mozilla.org/testing/geckodriver/geckodriver/)
  - Usage
    - `python2 codeScrapper.py settingsfile`
      - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).
      - This script requires hacker rank credentials (provided in a JSON file).
        An [example credentials file can be found here](./creds/ex_hr_creds.json).
        No worries, these aren't real credentials. I would only store these locally
        and under password protection (e.g., require admin privs to access).
- [pasteExtract.py](./scripts/pasteExtract.py)
  - Description
    - codeScraper.py outputs .paste files (paste output from student submissions).
      This script takes that paste output and parses out the actual submission code.
  - Usage
    - `python2 pasteExtract.py settingsfile`
      - Settings are given by a json file (see [example](./scripts/scraper-settings-example.json)).

## Plagiarism Detection

I used the [Moss system](https://theory.stanford.edu/~aiken/moss/) for detecting plagiarism. Given a bunch of code files, Moss will analyze the given code, looking
for similar code. Moss has some built-in smarts for several languages. I won't get 
into how to use Moss here. For that, refer to their [website](https://theory.stanford.edu/~aiken/moss/). 

My workflow:

- First, poke around on the internet for solutions posted on stackoverflow, github,
  etc. You don't have to be too clever here. Pretend you are a student intending
  to copy code from the internet, and do the obvious searches. 
- Use both the student submissions and any solutions found online as input to Moss.
- Then comes the tedious bit of combing through high-similarity code comparisons.