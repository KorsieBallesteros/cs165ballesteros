from django.db import models
from datetime import datetime
from django.urls import reverse
from django.db.models.signals import post_save, pre_save
from django.db.models import Q 
# Create your models here.
'''
CREATE TABLE Organization(
    organization_name = varchar(200)
    organization_abbrv = varchar(20) Primary Key
);
'''
class Organization(models.Model):
    organization_name = models.CharField(max_length=200)
    organization_abbrv = models.CharField(max_length=20,primary_key=True)

    def __str__(self):
        return self.organization_name

class Student(models.Model):
    student_number = models.CharField(max_length=9)
    student_name = models.CharField(max_length=200)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    sex = models.CharField(max_length=6)
    student_email = models.CharField(max_length=200)
    student_contact_no = models.CharField(max_length=200)

    class Meta:
        unique_together = (("student_number","organization"))
    def __str__(self):
        return self.student_number
class Signatures(models.Model):
    list_id = models.AutoField(primary_key=True)
    representative = models.ForeignKey(Student,on_delete=models.CASCADE,null=True)
    signature = models.BooleanField()
    time_stamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.list_id

class Event(models.Model):
    event_name = models.CharField(max_length=200,primary_key=True)
    student_representative = models.ForeignKey(Student,on_delete=models.CASCADE)
    must_prereg = models.BooleanField()
    event_description = models.CharField(max_length=200)
    registration_fee = models.PositiveIntegerField()
    number_players_min = models.PositiveIntegerField()
    number_players_max = models.PositiveIntegerField()
    day_or_night = models.CharField(max_length=200)
    mini_category = models.CharField(max_length=200)
    first_points = models.DecimalField(max_digits=10,decimal_places=2)
    second_points = models.DecimalField(max_digits=10,decimal_places=2)
    third_points = models.DecimalField(max_digits=10,decimal_places=2)
    party_points = models.DecimalField(max_digits=10,decimal_places=2)
    list_id = models.ForeignKey(Signatures,on_delete=models.CASCADE,blank=True,null=True)
    event_rules = models.TextField()
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk':self.pk})
    def __str__(self):
        return self.event_name
class Activity(models.Model):
    activity = models.CharField(max_length=200)
    event_name = models.ForeignKey(Event,on_delete=models.CASCADE)
    activity_date = models.DateField(auto_now=False,auto_now_add=False)
    activity_time_start = models.TimeField(auto_now=False,auto_now_add=False)
    activity_time_end = models.TimeField(auto_now=False,auto_now_add=False)
    activity_venue = models.CharField(max_length=200)

    class Meta:
        unique_together = (("event_name","activity"))

    def __str__(self):
        return self.activity
class Participant(models.Model):
    event_name = models.ForeignKey(Event, on_delete=models.CASCADE)
    representative = models.ForeignKey(Student, on_delete=models.CASCADE,related_name = 'rep')
    player = models.ForeignKey(Student, on_delete=models.CASCADE,related_name = 'part' )
    role = models.CharField(max_length=200)
    time_stamp_created = models.DateTimeField(auto_now_add=True)
    signature_list_id = models.ForeignKey(Signatures, on_delete=models.CASCADE,null=True) #approved by hosting organization
    class Meta:
        unique_together = (("event_name","representative","player"))

    def __str__(self):
        return '%s %s %s'%(self.event_name.event_name,self.representative.organization,self.player.student_name)

class Addendum(models.Model):
    event_name = models.ForeignKey(Event,on_delete=models.CASCADE)
    addendum_revision = models.TextField()
    addendum_reason = models.TextField()
    time_stamp_created = models.DateTimeField(auto_now_add=True)
    signature_list_id = models.ForeignKey(Signatures, on_delete=models.CASCADE,null=True) #approved by ESC
    def __str__(self):
        return self.addendum_revision
    def get_absolute_url(self):
        return reverse('event-detail', kwargs={'pk':self.pk})

class Consensus(models.Model):
    event_name = models.ForeignKey(Event,on_delete=models.CASCADE)
    representative = models.ForeignKey(Student,on_delete=models.CASCADE)
    consensus_revision = models.TextField()
    consensus_reason = models.TextField()
    time_stamp_created = models.DateTimeField(auto_now_add=True)
    signature_list_id = models.ForeignKey(Signatures,on_delete=models.CASCADE,null=True) #approved by ALL participating organization in the said event

    def __str__(self):
        return self.consensus_revision

class Scoresheet(models.Model):
    event_name = models.ForeignKey(Event,on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE)
    E_rank = models.PositiveIntegerField()

    def __str__(self):
        return self.E_rank

#Creates a new signature object for a newly rergistered organization and links this object to subsequent entries for an entry of that organization for a said event
def new_participant_from_org_pre(sender,instance,**kwargs):
    from_same_organization=Participant.objects.filter(Q(event_name__event_name=instance.event_name) & Q(representative__student_number=instance.representative))
    if len(from_same_organization) == 0:
        new_sig = Signatures.objects.create(signature=False)
        instance.signature_list_id = Signatures.objects.get(list_id=new_sig.list_id)
        #print('new entry: ',instance.signature_list_id.list_id)
    else:
        curr_sig_id = Participant.objects.filter(Q(event_name__event_name=instance.event_name) & Q(representative__student_number=instance.representative)).distinct('signature_list_id').values('signature_list_id')
        
        for entry in curr_sig_id:
            if entry ['signature_list_id'] is not None:
                new_id = entry['signature_list_id']

        instance.signature_list_id = Signatures.objects.get(list_id = new_id)
        #print('old entry: ',instance.signature_list_id.list_id)

def new_addendum_pre(sender,instance,**kwargs):
    new_sig = Signatures.objects.create(signature=False)
    instance.signature_list_id = Signatures.objects.get(list_id=new_sig.list_id)

#auto matically signs the consensus for the organization opening a consensus
#def new_consensus_pre(sender,instance,**kwargs):
    #new_sig = Signatures.objects.create(signature=True,representative=Student.objects.get(student_number=instance.representative,organization=Organization.objects.get(organization_abbrv=request.user.get_username()) ) )
    #instance.signature_list_id = Signatures.objects.get(list_id=new_sig.list_id)
#def new_participant_from_org_post(sender,instance,**kwargs):
#def update_signatures_pre(sender,instance,**kwargs):
#    participants = Participant.objects.filter()

pre_save.connect(new_participant_from_org_pre, sender=Participant)
pre_save.connect(new_addendum_pre, sender=Addendum)
#pre_save.connect(new_consensus_pre, sender=Consensus)
#post_save.connect(new_consensus_post, sender=Consensus)