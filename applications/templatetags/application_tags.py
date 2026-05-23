from django import template

register = template.Library()

# Maps each status to a numeric position in the pipeline
STATUS_ORDER = {
    'applied':              1,
    'under_review':         2,
    'shortlisted':          3,
    'interview_scheduled':  4,
    'selected':             5,
    'rejected':             5,
    'withdrawn':            5,
}

@register.filter
def get_status_position(current_status, step_status):
    """
    Returns True if the step_status has been reached
    based on the current application status.
    Usage: {{ app.status|get_status_position:step_val }}
    """
    current_pos = STATUS_ORDER.get(current_status, 0)
    step_pos    = STATUS_ORDER.get(step_status, 0)
    return current_pos >= step_pos
