import course_tools
import canvasapi as ucfcanvas
import requests
import logging
import time
import csv
from typing import Union

canvas = ucfcanvas.Canvas("https://champlain.instructure.com", course_tools.api_key)

parent_course_subaccount_id = 21181

parent_courses = canvas.get_account(parent_course_subaccount_id).get_courses(
    include=["syllabus_body"]
)

for course in parent_courses:
    if "IDEA" in course.syllabus_body:
        print("Fixing Syllabus in", course.name, course.id)
        new_text = course.syllabus_body.replace("IDEA", "VOICE")
        course.update(course={"syllabus_body": new_text})
