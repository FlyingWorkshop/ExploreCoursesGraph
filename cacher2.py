import pathlib
import json

import explorecourses
from tqdm import tqdm

import utils


YEARS = ["2019-2020", "2020-2021", "2021-2022"]


def get_prereqs(course: explorecourses.Course) -> list[int]:
    prereq_names = utils.get_prereqs(course)
    prereq_ids = utils.get_course_ids(prereq_names, course.year)
    prereqs = set(int(elem) for elem in prereq_ids)
    return list(prereqs)


def get_course_data(course: explorecourses.Course) -> dict:
    """
    Removes certain large attrs of explorecourses.Course objects to make caching easier
    Adds prerequisite information to the data
    """
    course_data = course.__dict__

    # remove large attrs with custom typing that are hard to cache
    del course_data["sections"]
    del course_data["tags"]
    del course_data["attributes"]
    del course_data["objectives"]

    # add prereq data
    course_data["prerequisites"] = get_prereqs(course)
    return course_data

def not_offered(course: explorecourses.Course) -> bool:
    for attr in course.attributes:
        if str(attr) == "NQTR::NOTTHIS":
            return True
    return False

def cache_courses(connect: explorecourses.CourseConnection, year: str):
    filepath = pathlib.Path(f"cache/{year}.json")

    data = {}
    print(f"Establishing connection for {year}...")
    courses = connect.get_courses_by_query(query="all courses", year=year)  # this step may take a while
    print("Connection established!")

    for course in tqdm(courses):
        if not_offered(course):
            continue
        data[course.course_id] = get_course_data(course)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    pathlib.Path("cache").mkdir(parents=True, exist_ok=True)
    connect = explorecourses.CourseConnection()
    for year in YEARS:
        cache_courses(connect, year)
