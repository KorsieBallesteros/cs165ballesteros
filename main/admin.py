from django.contrib import admin
from .models import Student,Organization,Signatures,Event,Activity,Addendum,Consensus,Participant
from tinymce.widgets import TinyMCE
from django.db import models
# Register your models here.

class EventAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Event",{"fields": ["event_name", "event_description","student_participant"]}),
        ("Registration",{"fields":["must_prereg","registration_fee","number_players_min","number_players_max"]}),
        ("Other Details",{"fields":["day_or_night","mini_category","list_id"]}),
        ("Scores",{"fields":["first_points","second_points","third_points","party_points"]}),
        ("Event Rules",{"fields":["event_rules"]})
    ]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


admin.site.register(Student)
admin.site.register(Organization)
admin.site.register(Event,EventAdmin)
admin.site.register(Signatures)
admin.site.register(Activity)
admin.site.register(Participant)
admin.site.register(Addendum)
admin.site.register(Consensus)

#temp =  Student.objects.create(student_number='201359724',student_name='Ian Maulion',sex='M',student_email='itmaulion@upd.edu.ph',student_contact_no='09999999999')
