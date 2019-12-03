from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Event,Addendum,Consensus,Participant
class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username","email","password1","password2")
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
class searchRules(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_name']
class NewAddendumForm(forms.ModelForm):
    class Meta:
        model = Addendum
        fields = ("addendum_revision","addendum_reason")

class NewConsensusForm(forms.ModelForm):
    representative = forms.CharField()
    class Meta:
        model = Consensus
        fields = ("consensus_revision","consensus_reason")

class JoinEventForm(forms.ModelForm):
    representative = forms.CharField()
    participants = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'eg: 202512345:role1,202512346:role2,...2025abcde:roleN'}))
    event_name = forms.CharField()
    class Meta:
        model = Participant
        fields = ('representative',)
class UpdateEventForm(forms.ModelForm):

    must_prereg = forms.CharField(required=False)
    event_description = forms.CharField(required=False)
    registration_fee = forms.IntegerField(required=False)
    number_players_min = forms.IntegerField(required=False)
    number_players_max = forms.IntegerField(required=False)
    day_or_night = forms.CharField(required=False)
    mini_category = forms.CharField(required=False)
    first_points = forms.DecimalField(required=False)
    second_points = forms.DecimalField(required=False)
    third_points = forms.DecimalField(required=False)
    party_points = forms.DecimalField(required=False)
    event_rules_and_guidelines = forms.CharField(required=False)
    class Meta:
        model = Event
        fields = ("event_name",)