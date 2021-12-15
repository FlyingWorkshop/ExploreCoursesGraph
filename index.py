import json
import os
import time
import re

import explorecourses

import utils

CACHE_FOLDER = "data"
CONNECT = explorecourses.CourseConnection()


def _set_up_cache(year: str, filename: str) -> (str, bool):
    """
    Makes the relevant directories. If a cached file already exists, print
    out information about when it was last cached and prompt the user about
    overwriting the cache with new data. Returns a boolean indicating whether
    the existing cache should be overwritten. If no cache exists, this function
    returns True by default.

    Returns two arguments. The 1st is the filepath; the 2nd is a boolean that
    indicates whether we should cache fresh data.
    """
    # set up dirs
    dirpath = os.path.join(CACHE_FOLDER, year)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    filepath = os.path.join(dirpath, filename)

    # check if filepath already cached
    if os.path.exists(filepath):
        # TODO: fix time message
        print(f"Warning: a file already exists at '{filepath}'.")
        print("Last modified: %s" % time.ctime(os.path.getmtime(filepath)))  # snippet modified from: https://www.w3resource.com/python-exercises/python-basic-exercise-64.php
        print("Created: %s" % time.ctime(os.path.getctime(filepath)))
        while (inp := input(f"Would you like to overwrite '{filepath}' [y|n]: ")) not in ("y", "n"):
            continue
        if inp == "n":
            print("No new data was cached.")
            return filepath, False
    print("Caching new data...")
    return filepath, True


def cache_course_ids(year):
    filepath, should_cache = _set_up_cache(year, "course_ids.json")
    if not should_cache:
        return

    # build index
    seen = set()
    index = {}
    courses = CONNECT.get_courses_by_query("all courses", year=year)
    for course in courses:
        key = course.course_id
        if key in seen:
            continue
        seen.add(key)
        value = utils.extract_aliases(course)
        if value:
            index[key] = value

    # cache index
    with open(filepath, "w") as f:
        json.dump(index, f, indent=4)


def cache_departments(year: str):
    filepath, should_cache = _set_up_cache(year, "departments.json")
    if not should_cache:
        return

    index = {}
    for school in CONNECT.get_schools(year):
        for dept in school.departments:
            index[dept.code] = dept.name

    with open(filepath, "w") as f:
        json.dump(index, f, indent=4)


def cache_suffixes(year: str):
    filepath, should_cache = _set_up_cache(year, "suffixes.json")
    if not should_cache:
        return

    suffixes = set()
    for course in CONNECT.get_courses_by_query("all courses", year):
        s = course.code.removeprefix(course.subject)
        m = re.search(r"[A-Z]", s)
        if m:
            i = m.start()
            suffix = s[i:]
            if "." in suffix:  # ignore weird edge cases (e.g. "UGXFER SME2.3: GER SME 2 SUBSTITUTION (3RD)")
                continue
            suffixes.add(suffix)

    with open(filepath, "w") as f:
        json.dump(list(suffixes), f, indent=4)


if __name__ == "__main__":
    cache_course_ids("2019-2020")
    # cache_suffixes("2021-2022")
    # load_course_ids("2021-2022")
