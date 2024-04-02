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

    # Copy Course adjusting dates
    parent_subaccount = canvas.get_account(parent_course_subaccount_id)
    name = master_course.name.replace("MASTER", "PARENT")
    course_code = master_course.course_code.replace("MASTER", "PARENT")
    new_course = parent_subaccount.create_course(
        course={"name": name, "course_code": course_code}
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
