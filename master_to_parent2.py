import course_tools
import canvasapi as ucfcanvas

canvas = ucfcanvas.Canvas("https://champlain.instructure.com", course_tools.api_key)

def convert_course_master_to_parent(course_id: int, parent_subaccount):
    """Convert a course from master to parent

    Args:
        course_id (int): The course id
        parent_subaccount:
    """
    master_course = 


default_term_id = course_tools.termid_from_name("Default Term")

all_master_courses = course_tools.get_course_ids(0, 14656, has_users=False)
