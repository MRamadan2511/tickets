from django.utils import timezone
from .models import Ticket, NewUser

def update_overdue_tickets():
    now = timezone.now()
    overdue_tickets = Ticket.objects.filter(status='OPEN', updated__lt=now, created__lt=now)
    for ticket in overdue_tickets:
        print(ticket.id)
        ticket.status = 'OVERDUE'
        ticket.save()
        admin_user = NewUser.objects.get(user='Admin')
        ticket.log_update(admin_user,
                                 f"Ticket uodated to overdue because there is no update for x mint")

        
   