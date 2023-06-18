# main/cron.py
from django_cron import CronJobBase, Schedule
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from .models import Ticket

class UpdateOverdueTickets(CronJobBase):
    RUN_EVERY_MINS = 1 # run every minute
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'main.update_overdue_tickets'    # a unique code

    def do(self):
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        tickets = Ticket.objects.filter(status__in=['OPEN', 'IN PROGRESS', 'WAITING'], closed_date=None, updated__lte=one_minute_ago)
        for ticket in tickets:
            ticket.status = 'OVERDUE'
            ticket.save()
            
# Successfully installed django-background-tasks-1.2.5 django-compat-1.0.15