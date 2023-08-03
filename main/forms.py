
from django import forms
from django.contrib.auth.models import User

from .models import Ticket, Comment


class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class TicketCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # get the user from the kwargs
        super().__init__(*args, **kwargs)
        if user:
            # define the custom field labels for the user
            if user.is_courier:
                self.fields['order_id'].label = 'رقم الاوردر'
                self.fields['description'].label = 'التفاصيل'

            else:
                self.fields['order_id'].label = 'Order ID'
                self.fields['description'].label = 'Description'


    class Meta:
        model = Ticket
        fields = ('order_id', 'description', 'post_image' ,)
        labels = {
            "post_image": ""
        }


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('warehouse', 'tag_to', )
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # self.fields['assigned_to'].queryset = User.objects.filter(is_active=True)
    #     if not User.is_superuser:
    #         # self.fields['warehouse'].disabled = True
    #         # self.fields['tag_to'].disabled = True
    

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment', 'comment_image']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'comment': '',
            'comment_image': ''
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if not comment:
            raise forms.ValidationError('Comment field cannot be empty')
        return comment

        
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['warehouse']

    def clean(self):
        cleaned_data = super().clean()
        print("Cleaned data:", cleaned_data)
        return cleaned_data
    

class TicketTagForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['tag_to']

    def clean(self):
        cleaned_data = super().clean()
        print("Cleaned data:", cleaned_data)
        return cleaned_data
    
class TicketFilterForm(forms.Form):
    STATUS_CHOICES = (
        ('', 'All'),
        ('OPEN', 'OPEN'),
        ('IN PROGRESS', 'IN PROGRESS'),
        ('WAITING', 'WAITING'),
        ('CLOSED', 'CLOSED'),
    )
    TEAM_CHOICES = (
        ('', 'All'),
        ('Last Mile', 'Last Mile'),
        ('Fleet', 'Fleet'),
        ('Quality', 'Quality'),
        ('FulFillment', 'FulFillment'),
        ('Security', 'Security'),
    )
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    tag_to = forms.ChoiceField(choices=TEAM_CHOICES, required=False)