from django import template

register = template.Library()

@register.filter
def status_class(status):
    if status == 'OPEN':
        return 'btn btn-dark'
    elif status == 'IN PROGRESS':
        return 'btn btn-warning'
    elif status == 'WAITING':
        return 'btn btn-info'
    elif status == 'CLOSED':
        return 'btn btn-success'
    elif status == 'OVERDUE':
        return 'btn btn-danger'
    else:
        return 'btn btn-secondary'