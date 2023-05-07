
from django import forms
from django.contrib.auth.models import User

from .models import Ticket, Comment


class UserSettingsForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',)


class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('order_id', 'description', 'post_image' ,)
        labels = {
            "post_image": ""
        }


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ( 'tag_to', 'warehouse',)
        # widgets = {'warehouse': forms.TextInput(attrs={'required': False})}

    


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment','comment_image')

        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, field in self.fields.items():
            field.label = ""


# class AttachmentForm(forms.ModelForm):
#     class Meta:
#         model = Attachment
#         fields = ('file',)
