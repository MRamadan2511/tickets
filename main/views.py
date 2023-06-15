from django.shortcuts import render,redirect, get_object_or_404

from django.db.models import Count, Q,Sum
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import TicketCreateForm,CommentForm
from django.utils import timezone
from django.http import Http404,HttpResponseRedirect
from django.contrib import messages
import plotly.graph_objs as go
import plotly.offline as opy

from .data_summary import generate_ticket_summary
import pandas as pd

from .models import Ticket,User, Comment,UserProfile, NewUser
from .forms import TicketEditForm, WarehouseForm, TicketTagForm,TicketFilterForm


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView,FormView
from django.views.generic import DetailView, ListView

from django.urls import reverse_lazy



def home(request):
    test = 5*5
    return render(request, 'base.html', context={'test':test})


def dashboard(request):
    tickets =  Ticket.objects.all()
    
    # tic_open = Ticket.objects.filter(status = 'OPEN').count()
    status_counts = Ticket.objects.values('status').annotate(total=Count('status'))
    status_labels = [s['status'] for s in status_counts]
    status_values = [s['total'] for s in status_counts]
    status_chart = opy.plot([go.Pie(labels=status_labels, values=status_values)])


    return render(request, 'dashboard.html', context={'tickets':tickets, 'status_chart': status_chart})


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


class TicketListView(ListView):
    model = Ticket
    template_name = 'inbox.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.get_queryset(user=user)
        status = self.request.GET.get('status')
        tag_to = self.request.GET.get('tag_to')

        if status:
            queryset = queryset.filter(status=status)
        if tag_to:
            queryset = queryset.filter(tag_to=tag_to)
        else:
            if user.is_courier:
                queryset = queryset.filter(owner=user)
            elif user.is_wh_manager or user.is_team_leader:
                queryset = queryset.filter(Q(owner=user) | Q(warehouse=user.wh))

         # Calculate the count of filtered tickets
        count = queryset.count()

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TicketFilterForm(self.request.GET)

        df = pd.DataFrame(generate_ticket_summary(self.get_queryset()))
    
        context['ticket_count'] = len(df)
        context['open_count'] = len(df[df['status']=='OPEN']) 
        context['closed_count'] = len(df[df['status']=='closed'])
        context['tag_to_count'] = len(df[df['tag_to']=='Last Mile']) 



  
        return context

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'detail.html'
    context_object_name = 'ticket'

    
    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.get_queryset(user)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        comments = Comment.objects.filter(ticket=self.object)
        context['comments'] = comments
        context['form'] = CommentForm()

        user = self.request.user

        if self.object.can_edit_warehouse(user):
            warehouse_form = WarehouseForm(initial={'warehouse': self.object.warehouse})
            context['warehouse_form'] = warehouse_form

        if self.object.can_edit_tag_to(user):
            tag_form = TicketTagForm(initial={'tag_to': self.object.tag_to})
            context['tag_form'] = tag_form

        return context
    
    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.user = self.request.user
            comment.save()
        return redirect('ticket_detail', pk=ticket.pk)
    
class TicketCommentView(FormView):
    template_name = 'ticket_comment.html'
    form_class = CommentForm

    def form_valid(self, form):
        # Get the Ticket object based on the URL parameter
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'])
        
        # Create a new Comment object from the form data
        comment = form.save(commit=False)
        comment.user = self.request.user
        print(comment.user)
        comment.ticket = ticket
        comment.save()

        return redirect('ticket_detail', pk=ticket.pk)

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.kwargs['pk']})


class TicketUpdateWarehouseView(UpdateView):
    model = Ticket
    fields = ['warehouse']
    template_name_suffix = '_update_warehouse_form'
    success_url = reverse_lazy('ticket_detail')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.wh_editable = False
        ticket.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.can_edit_warehouse(user):
            obj.wh_editable = True
            obj.save()
            return obj
        else:
            raise Http404("You don't have permission to access this page.")
        

    def get_queryset(self):
        user = self.request.user
        return Ticket.objects.get_queryset(user=user)

class TicketUpdateTagToView(UpdateView):
    model = Ticket
    fields = ['tag_to']
    template_name_suffix = '_update_tag_form'
    success_url = reverse_lazy('ticket_detail')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.object
        return kwargs

    def get_success_url(self):
        return reverse_lazy('ticket_detail', kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        if obj.can_edit_tag_to(user):
            # obj.wh_editable = True
            obj.save()
            return obj
        else:
            raise Http404("You don't have permission to access this page.")




# def update_wh_tag(request, ticket_id):
#     wh_list = Ticket.WAREHOUSE_CHOICES
#     team_tag_list = Ticket.TEAM_CHOICES
#     ticket = get_object_or_404(Ticket, pk=ticket_id)
  
#     if request.method == 'POST':
#         form = TicketEditForm(request.POST or None , request.FILES, instance=ticket, initial={'warehouse': ticket.warehouse, 'tag_to': ticket.tag_to,},)
#         if 'update' in request.POST:
#             print("update")
#             print(form.errors )
#             if request.user ==  request.user.is_team_leader:
#                     print(request.user)
#                     form.initial['warehouse']=ticket.warehouse
#                     print("ok222")
#             if form.is_valid():
#                 print("ok valid")
#                 if request.user !=  request.user.is_team_leader:
#                     form.initial['warehouse']=ticket.warehouse
#                     print("ok222")
#                 ticket.warehouse = form.cleaned_data['warehouse']
#                 ticket.tag_to = form.cleaned_data['tag_to']
#                 form.save()
#                 messages.success(request, "WareHouse & Tag  Updated Successfuly")
#                 return redirect('ticket_detail', ticket_id=ticket.id)
        
#     else:
#         form = TicketEditForm( initial={'warehouse': ticket.warehouse, 'tag_to': ticket.tag_to,},  instance=ticket)
#     return render(request,'wh_update.html',
#                     {'ticket': ticket,
#                     'form':form,
#                     'wh_list': wh_list,
#                     'team_tag_list':team_tag_list,})


# def ticket_detail_view(request, ticket_id):
#     wh_list = Ticket.WAREHOUSE_CHOICES
#     team_tag_list = Ticket.TEAM_CHOICES
    
#     ticket = get_object_or_404(Ticket, pk=ticket_id)
#     comments = Comment.objects.filter(ticket=ticket)

    
#     #comment Data
#     new_comment = None
#     # Comment posted0
#     if request.method == 'POST':
#         comment_form = CommentForm(request.POST, request.FILES)
#         if comment_form.is_valid():
#             new_comment = comment_form.save(commit=False)
#             new_comment.ticket = ticket
#             new_comment.user = request.user
#             new_comment.save()
#             messages.info(request, "Comment added successfully ")
#             return redirect('ticket_detail', ticket_id=ticket.id)
#     else:        
#         comment_form = CommentForm()

#     return render(request,'ticket_detail.html',
#                   {'ticket': ticket,
#                    'wh_list': wh_list,
#                     'team_tag_list':team_tag_list,
#                    'comments': comments,
#                    'new_comment': new_comment,
#                    'comment_form':comment_form,
                   
#                    })