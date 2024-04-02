import course_tools
import canvasapi as ucfcanvas
import requests
import logging

canvas = ucfcanvas.Canvas("https://champlain.instructure.com", course_tools.api_key)

parent_course_subaccount_id = 21181


def convert_course_master_to_parent(course_id: int, parent_subaccount):
    """Convert a course from master to parent

    Args:
        course_id (int): The course id
        parent_subaccount:
    """
    # Get Course
    master_course = canvas.get_course(course_id)

    # Create a new course in the parent subaccount
    parent_subaccount = canvas.get_account(parent_course_subaccount_id)
    name = master_course.name.replace("MASTER", "PARENT")
    course_code = master_course.course_code.replace("MASTER", "PARENT")
    new_course = parent_subaccount.create_course(
        course={"name": name, "course_code": course_code}
    )

    # Create a content migration
    migration = new_course.create_content_migration(
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

    """
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
    """


default_term_id = course_tools.termid_from_name("Default Term")

all_master_courses = course_tools.get_course_ids(
    default_term_id, 14656, has_users=False
)

# Test for a single master course
convert_course_master_to_parent(all_master_courses[10], parent_course_subaccount_id)
