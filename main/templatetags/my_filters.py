from django import template

register = template.Library()

@register.filter
def status_class(status):
    if status == 'OPEN':
        return 'btn btn-warning'
    elif status == 'IN PROGRESS':
        return 'btn btn-primary'
    elif status == 'WAITING':
        return 'btn btn-info'
    elif status == 'DONE':
        return 'btn btn-success'
    else:
        return 'btn btn-secondary'