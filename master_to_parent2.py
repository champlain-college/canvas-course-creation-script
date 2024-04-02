import course_tools
import canvasapi as ucfcanvas
import requests
import logging
import time
import csv

canvas = ucfcanvas.Canvas("https://champlain.instructure.com", course_tools.api_key)

parent_course_subaccount_id = 21181


def convert_course_master_to_parent(course_id: int):
    """Convert a course from master to parent

    Args:
        course_id (int): The course id
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
    migration = parent_course.create_content_migration(
        migration_type="course_copy_importer",
        settings={
            "source_course_id": master_course.id,
            # We don't need to shift dates in this case but will have to in the parent to term copy
            # For parent to term copy
            # "date_shift_options": {
            #    "shift_dates": True,
            #    "old_start_date": "2024-05-06T00:00:00Z",
            #    "new_start_date": "2023-01-09T04:00:00Z",
            # },
        },
    )

    return parent_course.id


def remove_idea_stuff(parent_course_id):
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
        remove_idea_stuff(parent_course_id)


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


default_term_id = course_tools.termid_from_name("Default Term")
master_account_id = 14656
all_master_courses = canvas.get_account(master_account_id).get_courses()


# UNCOMMENT WHEN YOU WANT TO RUN THE WHOLE SCRIPT
# RUN THE FIRST LINE BY ITSELF THEN A FEW HOURS LATER RUN THE REST
# new_parent_ids = migrate_every_master_to_parent(all_master_courses)
# STOP HERE AND WAIT FOR MIGRATIONS TO COMPLETE
# remove_idea_from_all(new_parent_ids)
# generate_spreadsheet(new_parent_ids)


# Test creation of single master course with content migration
# Migrates the 10th course in the list
new_parent_course_id = convert_course_master_to_parent(all_master_courses[10])
print("pausing for 4 minutes for migration to complete")
time.sleep(240)
# Test removal of IDEA stuff
remove_idea_stuff(new_parent_course_id)
