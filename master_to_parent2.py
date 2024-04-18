import course_tools
import canvasapi as ucfcanvas
import requests
import logging
import time
import csv
from typing import Union

canvas = ucfcanvas.Canvas("https://champlain.instructure.com", course_tools.api_key)

parent_course_subaccount_id = 21181


def convert_course_master_to_parent(
    course_id: Union[int, str], previous_term_name: str = ""
):
    """Convert a course from master to parent

    Args:
        course_id (int): The course id
        previous_term_name (str): The name of the previous term. If empty dates are not shifted
    Returns: New parent course id
    """
    # Get Course
    master_course = canvas.get_course(course_id)

    # Create a new course in the parent subaccount
    parent_subaccount = canvas.get_account(parent_course_subaccount_id)
    name = master_course.name.replace("MASTER", "PARENT")
    course_code = master_course.course_code.replace("MASTER", "PARENT")
    parent_course = parent_subaccount.create_course(
        course={"name": name, "course_code": course_code}
    )

    # Create a content migration
    if previous_term_name:
        # shift the dates to Summer 2024
        old_term_id = course_tools.termid_from_name(previous_term_name)
        root_account = canvas.get_account(283)
        old_term = root_account.get_enrollment_term(old_term_id)
        course_settings = {
            "source_course_id": master_course.id,
            "date_shift_options": {
                "shift_dates": True,
                "old_start_date": old_term.start_at,
                "new_start_date": "2024-05-06T00:00:00Z",
            },
        }

    else:
        course_settings = {"source_course_id": master_course.id}

    migration = parent_course.create_content_migration(
        migration_type="course_copy_importer", settings=course_settings
    )

    # Reenroll all people in the previous master course. This time they should all be observers
    for user in master_course.get_users():
        parent_course.enroll_user(user.id, enrollment={"type": "ObserverEnrollment"})

    return parent_course.id


def replace_idea_with_voice(parent_course_id):
    """Remove references to IDEA survey from parent course
    It takes quite a while for the content migration to complete,
    so we can't do this until the migration is complete.
    Create and migrate the course first, then run this function.
    """
    parent_course = canvas.get_course(parent_course_id)

    # Remove the IDEA stuff
    for external_tool in parent_course.get_external_tools():
        if "IDEA" in external_tool.name:
            external_tool.delete()

    modules = parent_course.get_modules()
    # Look for items in modules containing "IDEA" and remove them
    for module in modules:
        for module_item in module.get_module_items():
            if "IDEA" in module_item.title:
                module_item.delete()

    announcements = parent_course.get_discussion_topics(only_announcements=True)
    for announcement in announcements:
        if "IDEA" in announcement.title:
            announcement.delete()

    assignment_groups = parent_course.get_assignment_groups()
    for group in assignment_groups:
        if "IDEA" in group.name:
            group.name.replace("IDEA", "VOICE")

    assignments = parent_course.get_assignments()
    for assignment in assignments:
        if "IDEA" in assignment.name:
            assignment.delete()

    # TODO
    # In the module named “Instructor Resources” search for a page where the name contains “Course Support Materials” and rename that page “Instructors - READ ME”
    modules = parent_course.get_modules()
    for module in modules:
        if "Instructor Resources" in module.name:
            for module_item in module.get_module_items():
                if "Course Support Materials" in module_item.title:
                    module_item.edit(module_item={"title": "Instructors - READ ME"})
    # In the text of the syllabus, replace the word “IDEA” (all caps) with “VOICE” (all caps)
    syllabus = parent_course.get_syllabus()
    if "IDEA" in syllabus:
        syllabus.replace("IDEA", "VOICE")
        parent_course.edit(course={"syllabus_body": syllabus})
    # Create a placeholder assignment “VOICE Course Evaluation”
    parent_course.create_assignment(
        assignment={"name": "VOICE Course Evaluation", "published": True}
    )


def migrate_every_master_to_parent(master_courses):
    """Copy all master courses to parent courses and migrate the content

    Args:
        master_courses (list): List of master course objects from canvasapi
    Returns: List of parent course ids
    """
    parent_course_ids = []
    for course_id in master_courses.ids:
        parent_course_ids.append(convert_course_master_to_parent(course_id))

    return parent_course_ids


def remove_idea_from_all(parent_course_ids):
    for parent_course_id in parent_course_ids:
        replace_idea_with_voice(parent_course_id)


def generate_spreadsheet(parent_course_ids):
    """Generate a .csv listing all parent courses
    Fields for .csv: course_name, course_code, course_id"""
    with open("parent_courses.csv", "w", newline="") as csvfile:
        fieldnames = ["course_name", "course_code", "course_id"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for parent_course_id in parent_course_ids:
            parent_course = canvas.get_course(parent_course_id)
            writer.writerow(
                {
                    "course_name": parent_course.name,
                    "course_code": parent_course.course_code,
                    "course_id": parent_course_id,
                }
            )


def read_parent_ids_from_csv():
    parent_ids = []
    with open("parent_courses.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            parent_ids.append(row["course_id"])
    return parent_ids


def migrate_master_to_parent_from_csv(filename):
    """Reads the course ids and term names from a csv file and migrates the courses to parent courses"""
    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)
        return [
            convert_course_master_to_parent(
                row["course_id"], row["Watermark Project Terms"]
            )
            for row in reader
        ]


default_term_id = course_tools.termid_from_name("Default Term")
master_account_id = 14656
all_master_courses = canvas.get_account(master_account_id).get_courses()


# UNCOMMENT WHEN YOU WANT TO RUN THE WHOLE SCRIPT
# RUN THE FIRST LINE BY ITSELF THEN A FEW HOURS LATER RUN THE REST
# new_parent_ids = migrate_master_to_parent_from_csv("parent_course_list.csv")
# generate_spreadsheet(new_parent_ids)
# STOP HERE AND WAIT FOR MIGRATIONS TO COMPLETE
# parent_ids = read_parent_ids_from_csv()
# remove_idea_from_all(new_parent_ids)
#


# Test creation of single master course with content migration
# Migrates the 10th course in the list
# new_parent_course_id = convert_course_master_to_parent(all_master_courses[10])
# print("pausing for 4 minutes for migration to complete")
# time.sleep(240)
# Test removal of IDEA stuff
# remove_idea_stuff(new_parent_course_id)


# Erase all parent courses from parent sub-account
"""
parent_subaccount = canvas.get_account(parent_course_subaccount_id)
for course in parent_subaccount.get_courses():
    if "PARENT" in course.name:
        print(course.name)
    #    course.delete()
    else:
        print(course.name, " - Not a parent course")
"""
