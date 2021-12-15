import re

import explorecourses
import graphviz

import cacher
import utils


class Graph:
    def __init__(self, year: str):
        self.year = year

        connect = explorecourses.CourseConnection()
        cacher.cache_course_ids(connect, year)
        cacher.cache_departments(connect, year)
        cacher.cache_prereqs(connect, year)

    def graph_dept(self, school: str, dept):
        prereqs = utils.load_prereqs(self.year)
        processed = self._process(prereqs[school][dept], self.year)
        return self.display(processed)

    @staticmethod
    def _process(data: dict[str: list[str]], year: str) -> dict[str: list[str]]:
        index = utils.load_course_ids(year)
        processed = {}
        for course_id, prereq_ids in data.items():
            course_name = index[course_id][0]
            processed[course_name] = []
            for prereq_id in prereq_ids:
                prereq_name = index[prereq_id][0]
                processed[course_name].append(prereq_name)
        return processed

    @staticmethod
    def display(processed: dict[str: str]):
        g = graphviz.Digraph()
        for course_name, prereq_names in processed.items():
            for prereq_name in prereq_names:
                g.edge(course_name, prereq_name)
        return g
