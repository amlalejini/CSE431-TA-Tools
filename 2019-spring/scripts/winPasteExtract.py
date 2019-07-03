from bs4 import BeautifulSoup
import json, os, time, errno, sys

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

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

LANG_TO_EXT = {"python3": "py",
               "python2": "py",
               "python": "py",
               "pypy2": "py",
               "pypy3": "py",
               "pypy": "py",
               "cpp": "cc",
               "cpp14": "cc",
               "c": "cc",
               "java8": "java",
               "java": "java",
               "php": "php",
               "ruby": "rb",
               "csharp": "cc",
               "ada": "ada"
               }
LANG_TO_COMMENT = {"python3": "#",
               "python2": "#",
               "python": "#",
               "pypy2": "#",
               "pypy3": "#",
               "cpp": "//",
               "cpp14": "//",
               "c": "//",
               "java8": "//",
               "java": "//",
               "php": "//",
               "ruby": "//",
               "csharp": "//",
               "ada": "--"
               }

def main():
    settings = None
    scrapings_dir = None # Where's the paste? MUST EAT PASTE.
    code_dir = None      # Where should I spit out the code?

    # Grab args from command line.
    if len(sys.argv) < 2:
        print "No settings file?"
        exit(-1)
    try:
        with open(sys.argv[1], "r") as fp:
            settings = json.load(fp)
    except:
        print "Could not load given settings file."
        exit(-1)

    detection_ws = settings["detection_workspace"]
    assignment_name = settings["assignment_name"]
    scrapings_dir = os.path.join(detection_ws, assignment_name, "scrapings")
    code_dir = os.path.join(detection_ws, assignment_name, "code")

    mkdir_p(code_dir)
    students = [d for d in os.listdir(scrapings_dir) if "." not in d]

    for student in students:
        print "Student: %s" % student
        student_dir = os.path.join(scrapings_dir, student)
        # Load metadata.
        student_meta = None
        with open(os.path.join(student_dir, "student_metadata.json"), "r") as fp:
            student_meta = json.load(fp)
        # Get list of problems for student.
        problems = [d for d in os.listdir(student_dir) if ".paste" in d]
        for problem in problems:
            print "\tProblem: %s" % problem
            problem_name = problem.split(".")[0]
            # What language is the problem submission written in?
            lang = student_meta["submissions"][problem_name]["language"]
            days = int(student_meta["submissions"][problem_name]["time"]) / 1440.0 # Xmin * 1hr/60min * 1day/24hr
            print "\t  - %s" % lang
            if not lang in LANG_TO_EXT:
                print "OH NOES! I don't recognize that language!"
                exit(-1)
            pasty = None
            with open(os.path.join(student_dir, problem), "r") as fp:
                pasty = fp.read().split("\n")
            fcode = False
            source_lines = []
            ext = None
            # for line in pasty:
            #     line = line.strip("\n")
            #     line = line.strip("\r")
            #     if "Join us on IRC at #hackerrank" in line:
            #         break
            #     elif fcode:
            #         if len(line) > 0:
            #             if line.isalnum(): continue
            #             else:
            #                 source_lines.append(line.decode('utf-8').encode('ascii', errors='ignore'))
            #     elif "Open in editor" in line:
            #         fcode = True
            #### Had to do this to fix the fix that broke the thing - Riley
            for line in pasty:
                line = line.strip("\n")
                line = line.strip("\r")
                if len(line) > 0:
                    if line.isalnum(): continue
                    else:
                        source_lines.append(line.decode('utf-8').encode('ascii', errors='ignore'))
            with open(os.path.join(code_dir, "%s__%s.%s" % (student, problem_name, LANG_TO_EXT[lang])), "w") as fp:
                fp.write("%sTime Stamp:%f\n" % (LANG_TO_COMMENT[lang], days))
                fp.write("\n".join(source_lines))

if __name__ == "__main__":
    main()
