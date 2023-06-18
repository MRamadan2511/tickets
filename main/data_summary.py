import pandas as pd

from .models import Ticket

tickets = Ticket.objects.all()

def generate_ticket_summary(queryset):
    df = pd.DataFrame(columns=['order_id','status','warehouse','assigned_to','tag_to'])
        
    for ticket in queryset:      
        series = pd.Series({
            'order_id': ticket.order_id,
            'status': ticket.status,  
            'warehouse': ticket.warehouse,  
            'assigned_to': ticket.assigned_to.user if ticket.assigned_to else None,     
            'tag_to': ticket.tag_to  
        })   
        df = df._append(series, ignore_index=True)
        
    return df