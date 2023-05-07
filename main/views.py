from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import TicketCreateForm,CommentForm
from django.utils import timezone
from django.http import Http404,HttpResponseRedirect
from django.contrib import messages

from .models import Ticket,User, Comment,UserProfile, NewUser
from .forms import TicketEditForm


def home(request):
    test = 5*5
    return render(request, 'base.html', context={'test':test})


def is_have_access(user):
    '''Validate if user have access to edit ticket'''
    if user.is_superuser:
        print(user)
        return user
    return user.groups.filter(name='courier').exists()



@login_required
def ticket_create_view(request):
    ticket_create_form = TicketCreateForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        if ticket_create_form.is_valid():
            ticket_create_form  =ticket_create_form.save(commit=False)
            ticket_create_form.owner = request.user
            ticket_create_form.warehouse = request.user.wh
            ticket_create_form.save()
            return redirect('ticket_detail', ticket_create_form.pk)
 
    return render(request,'create_ticket.html',{'ticket_create_form': ticket_create_form, })

@login_required
def inbox_view(request):
    user = request.user
    tickets=None


    if user.is_superuser:
        tickets =  Ticket.objects.all()

    elif user.is_wh_manager or user.is_team_leader:

        newusers = NewUser.objects.get(user=user)
        tickets =  Ticket.objects.filter(owner=user) | Ticket.objects.filter(warehouse=getattr(newusers, 'wh' ))
    
    elif user.is_fleet:
        # newusers = NewUser.objects.get(user=user)
        tickets =  Ticket.objects.filter(owner=user) | Ticket.objects.filter(tag_to='Fleet')

    else:
        tickets =  Ticket.objects.filter(owner=user) 
  

    return render(request, 'inbox.html',context= 
                                            {"tickets": tickets,},
                                            )


def ticket_detail_view(request, ticket_id):
    wh_list = Ticket.WAREHOUSE_CHOICES
    team_tag_list = Ticket.TEAM_CHOICES
    ticket = get_object_or_404(Ticket, pk=ticket_id)
    comments = Comment.objects.filter(ticket=ticket)

    #Ticket Data
    if request.method == 'POST':
        form = TicketEditForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            print('OKKKK')
            new_warehouse = form.save(commit=False)
            new_warehouse.warehouse = form.cleaned_data['warehouse']
            new_warehouse.tag_to = form.cleaned_data['tag_to']
            new_warehouse.save()
            messages.success(request, "WareHouse & Tag  Updated Successfuly")
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketEditForm(instance=ticket)

    #comment Data
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.ticket = ticket
            new_comment.user = request.user
            new_comment.save()

            #Return to same page
            # return HttpResponseRedirect(request.path_info)
            messages.info(request, "Comment added successfully ")
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:        
        comment_form = CommentForm()

    return render(request,'ticket_detail.html',
                  {'ticket': ticket,
                   'form':form,
                   'wh_list': wh_list,
                   'team_tag_list':team_tag_list,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form':comment_form,
                   
                   })





  # #Filter if user has access to th GC Group
    # courier_group = Group.objects.get(name="courier").user_set.all()
    # if user in courier_group:
    #     tickets = Ticket.objects.filter(owner=user)

    # #Filter if user has access to th Team Leader Group or Crated by user
    # team_leader_group = Group.objects.get(name="team_leader").user_set.all()
    # if user in team_leader_group:
    #     newusers = NewUsers.objects.get(user=user)
    #     tickets =  Ticket.objects.filter(warehouse=getattr(newusers, 'warehouse' )
    #                                         ) | Ticket.objects.filter(owner=user)

    