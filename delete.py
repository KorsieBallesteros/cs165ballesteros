from django.contrib.auth.models import User
from main.models import Tutorial,Student,Organization,Signatures,Event,Activity,Addendum,Consensus,Participant
User.objects.exclude(username = 'admin').delete()
Event.objects.all().delete()
Organization.objects.all().delete()
Student.objects.all().delete()
Activity.objects.all().delete()
Participant.objects.all().delete()
Consensus.objects.all().delete()
Addendum.objects.all().delete()

