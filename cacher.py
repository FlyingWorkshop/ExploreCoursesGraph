import json
import os

from tqdm import tqdm
import explorecourses

import utils

CACHE_FOLDER = "data"


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
        stat = os.stat(filepath)
        print(f"Warning: a file already exists at '{filepath}'."
              f"Last modified: {stat.st_mtime}"
              f"Created: {stat.st_birthtime}")
        while (inp := input(f"Would you like to overwrite '{filepath}' [y|n]: ")) not in ("y", "n"):
            continue
        if inp == "n":
            print("No new data was cached.")
            return filepath, False
    print("Caching new data...")
    return filepath, True


def cache_course_ids(connect: explorecourses.CourseConnection, year):
    filepath, should_cache = _set_up_cache(year, "course_ids.json")
    if not should_cache:
        return

    # build index
    seen = set()
    index = {}
    courses = connect.get_courses_by_query("all courses", year=year)
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


def cache_departments(connect: explorecourses.CourseConnection, year: str):
    filepath, should_cache = _set_up_cache(year, "departments.json")
    if not should_cache:
        return

    index = {}
    for school in connect.get_schools(year):
        for dept in school.departments:
            index[dept.code] = dept.name

    with open(filepath, "w") as f:
        json.dump(index, f, indent=4)

def cache_prereqs(connect: explorecourses.CourseConnection, year: str):
    filepath, should_cache = _set_up_cache(year, "prereqs.json")
    if not should_cache:
        return

    data = {}

    schools_pbar = tqdm(connect.get_schools(year), desc="schools")
    for school in schools_pbar:
        data[str(school)] = {}
        schools_pbar.set_description(f"schools ({str(school)})")
        depts_pbar = tqdm(school.departments, desc="departments", leave=False)
        for dept in depts_pbar:
            data[str(school)][dept.code] = {}
            depts_pbar.set_description(f"departments ({dept.code})")
            courses = connect.get_courses_by_department(dept.code, year=year)
            courses_pbar = tqdm(courses, desc="courses", leave=False)
            for course in courses_pbar:
                courses_pbar.set_description(f"courses ({utils.make_course_name(course)})")
                prereqs = utils.get_prereqs(course)
                if prereqs:
                    prereq_ids = utils.get_course_ids(prereqs, year)
                    data[str(school)][dept.code][course.course_id] = prereq_ids

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    cache_prereqs(explorecourses.CourseConnection(), "2021-2022")
