from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User, AbstractBaseUser, PermissionsMixin,BaseUserManager
from datetime import datetime as tz
from django.utils import timezone
import pytz

# from django.utils.deconstruct import deconstructible

from phonenumber_field.modelfields import PhoneNumberField



class Company(models.Model):
    company_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created', ]

    def __str__(self):
        return f"{self.company_name}"

class Warehouse(models.Model):
    wh_name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created', ]

    def __str__(self):
        return f"{self.wh_name}"


    
class TagTeam(models.Model):
    tag = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, verbose_name='Company', on_delete=models.CASCADE)


    class Meta:
        ordering = ['created', ]

    def __str__(self):
        return f"{self.tag} -  {self.company} "



class CustomAccountManager(BaseUserManager):

    def create_superuser(self, user,  password, **other_fields):

        # other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        # if other_fields.get('is_staff') is not True:
        #     raise ValueError(
        #         'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(user, password, **other_fields)


    def create_user(self, user, password, **other_fields):

        user = self.model( user=user, **other_fields)
        user.set_password(password)
        user.save()
        return user


class NewUser(AbstractBaseUser, PermissionsMixin):
    user            = models.CharField(max_length=150, unique=True)
    # mobile          = PhoneNumberField()
    is_courier      = models.BooleanField(default=False)
    is_wh_manager   = models.BooleanField(default=False)
    is_team_leader  = models.BooleanField(default=False)
    is_manager      = models.BooleanField(default=False)
    is_staff        = models.BooleanField(default=False)
    is_active       = models.BooleanField(default=False)
    is_fleet        = models.BooleanField(default=False)
    company         = models.ForeignKey(Company,related_name='company', blank=True,null=True,
                              verbose_name='Company', on_delete=models.CASCADE)
    warehouse         = models.ForeignKey(Warehouse,related_name='warehouse', blank=True,null=True,
                              verbose_name='Warehouse', on_delete=models.CASCADE)
    objects = CustomAccountManager()
    
    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = []
    


class UserProfile(models.Model):  
    user = models.OneToOneField(NewUser,on_delete=models.CASCADE)  

   
    WAREHOUSE_CHOICES = (
        ('Mostorod', 'Mostorod'),
        ('Basatin', 'Basatin'),
        ('Haram', 'Haram'),
        ('Basous', 'Basous'),
        ('All', 'All'),
        )

    warehouse = models.CharField('warehouse',choices=WAREHOUSE_CHOICES, max_length=255,blank=True,null=True,)

    def __str__(self):  
          return "%s" % self.user 



class TicketManager(models.Manager):
    def get_queryset(self, user=None):
        if user is None:
            return super().get_queryset()
        if user.is_superuser:
            return super().get_queryset()
        elif user.is_courier:
            return super().get_queryset().filter(owner=user)
        elif user.is_wh_manager or user.is_team_leader:
            return super().get_queryset().filter(owner=user) | super().get_queryset().filter(warehouse=user.wh)
        else:
            return super().get_queryset().filter(owner=user)
        
class Ticket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'OPEN'),
        ('IN PROGRESS', 'IN PROGRESS'),
        ('WAITING', 'WAITING'),
        ('CLOSED', 'CLOSED'),
        ('OVERDUE', 'OVERDUE'),
    )
    WAREHOUSE_CHOICES = (
        ('Mostorod', 'Mostorod'),
        ('Basatin', 'Basatin'),
        ('Haram', 'Haram'),
        ('Basous', 'Basous'),
        ('All', 'All'),
        )

    TEAM_CHOICES = (
        ('Last Mile', 'Last Mile'),
        ('Fleet', 'Fleet'),
        ('Quality', 'Quality'),
        ('FulFillment', 'FulFillment'),
        ('Security', 'Security'),
    )

    TAGS = (
        ('Car Issue', 'Car Issue'),
        ('Discount Issue', 'Discount Issue'),
        ('Delay OR Failed', 'Delay OR Failed'),
        ('Partial Deliverey', 'Partial Deliverey'),
        ('Arrive Orders', 'Arrive Orders'),
    )

    order_id = models.IntegerField('Order ID',)

    owner = models.ForeignKey(NewUser,related_name='owner', blank=True,null=True,
                              verbose_name='Owner', on_delete=models.CASCADE)
    tag_to = models.CharField('Tag To',choices=TEAM_CHOICES, max_length=255,blank=True,null=True,)
    description = models.TextField('Description', blank=True, null=True)
    status = models.CharField('Status',choices=STATUS_CHOICES,max_length=255,
                              blank=True, null=True, default="OPEN")
    warehouse = models.CharField('Warehouse',choices=WAREHOUSE_CHOICES,max_length=255,blank=True,null=True,)
    post_image= models.ImageField(upload_to='image/post' ,blank=True, null=True,)
    closed_date = models.DateTimeField(blank=True, null=True)
    assigned_to = models.ForeignKey(NewUser,
                                    related_name='assigned_to', blank=True, null=True,
                                    verbose_name='Assigned to', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tag = models.CharField('Tag',choices=TAGS,max_length=255,
                              blank=True, null=True, default="None")
    
    wh_editable = models.BooleanField(default=False)

    objects = TicketManager()


    def save(self, *args, **kwargs):
        # check if the tag_to or assigned_to fields have changed
        if self.pk:
            original_ticket = Ticket.objects.get(pk=self.pk)
            if self.tag_to != original_ticket.tag_to or self.assigned_to != original_ticket.assigned_to:
                # update the status to "WAITING"
                self.status = "WAITING"
                # add a log entry
                admin_user = NewUser.objects.get(user='Admin')
                print("Change ticket status to waiting")
                self.log_update(user=admin_user,
                                 message=f"The ticket status was changed to WAITING because the {'' if self.tag_to == original_ticket.tag_to else 'tag_to '}{'and ' if self.tag_to != original_ticket.tag_to and self.assigned_to != original_ticket.assigned_to else ''}{'' if self.assigned_to == original_ticket.assigned_to else 'assigned_to '}fields were updated.")
            
        super().save(*args, **kwargs)


    def log_update(self, user, message):
        TicketLog.objects.create(ticket=self, user=user, message=message)


    def is_accessible_by_courier(self, user):
        return user.has_perm('user.is_courier') and self.owner == user


    def can_edit_warehouse(self, user):
        return  user.is_wh_manager or user.is_superuser
    
    def can_edit_tag_to(self, user):
        return user.is_team_leader or user.is_wh_manager or user.is_superuser
    

    class Meta:
        ordering = ['-updated', ]

    def __str__(self):
        return f"{self.order_id}"



class TicketLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    def __str__(self):
        return f"{self.ticket} - {self.user} - {self.message} @ {self.timestamp}"


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, verbose_name='Ticket', on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True,)
    user = models.ForeignKey(NewUser, blank=True, null=True, verbose_name='User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    comment_image= models.ImageField(upload_to='image/comment' ,blank=True, null=True,)


    def save(self, *args, **kwargs):
        if not self.pk:
            # If this is a new comment, update the assigned user of the ticket
            if not self.ticket.assigned_to and not self.user.is_courier:
                self.ticket.assigned_to = self.user
                self.ticket.save()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['modified', ]

    def __str__(self):
        return "%s" % (self.ticket.id)

    

    
