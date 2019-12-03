from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from .models import Student,Organization,Signatures,Event,Activity,Participant,Addendum,Consensus,Scoresheet
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from .forms import NewUserForm,searchRules
from django.db.models import Q 
from .forms import NewAddendumForm,NewConsensusForm,JoinEventForm,UpdateEventForm
from datetime import datetime
def homepage(request):
    print(Organization.objects.get(organization_abbrv='UPESC'))
    return render(request,"main/home.html",
                     {"students": Student.objects.all,
                      "organization": Organization.objects.all,
                      "signatures": Signatures.objects.all,
                      "events": Event.objects.all,
                      "activitys": Activity.objects.all,
                      "participants": Participant.objects.all,
                      "addendums": Addendum.objects.all,
                      "consensuss": Consensus.objects.all,
                      "scoresheet": Scoresheet.objects.all,
                      "admin": Organization.objects.get(organization_abbrv='UPESC')
                     })
                  
#"students":Student.objects.all
def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username') 
            messages.success(request, f"New Account Created: {username}" )
            login(request, user)
            messages.info(request,f"You are now logged in as {username}")
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}:{form.error_messages[msg]}")

        return render(request = request,
                  template_name = "main/register.html",
                  context={"form":form})
    form = NewUserForm
    return render(request = request,
                  template_name = "main/register.html",
                  context={"form":form})
def logout_request(request):
    logout(request)
    messages.info(request,"Logged out successfully")
    return redirect("main:homepage")
    
def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request, user)
                messages.info(request,f"You are now logged in as {username}")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password")
        else:
            messages.error(request,"Invalid username or password")
    

    form = AuthenticationForm()
    return render(request,"main/login.html",{"form":form})

# selects all events hosted by the organization
def myevents(request):
    username = request.user.get_username()
    match = Event.objects.filter(Q(student_representative__organization__organization_abbrv__icontains=username))
    my_events = Event.objects.filter()
    return render(request = request,
                  template_name="main/myevents.html",
                  context={"events": match,"admin": Organization.objects.get(organization_abbrv='UPESC') })


def search_rules(request):
    if request.method=='POST':
        srch = request.POST['srh']
        print(srch)
        if srch:
            match = Event.objects.filter(Q(event_name__icontains=srch)|
                                         Q(student_representative__organization__organization_abbrv__icontains=srch)
            )

            if match:
                return render(request,'main/events.html',{'event': match})
            else:
                messages.error(request,'no result found')
        else:
            return HttpResponseRedirect('/events/')

    return render(request,"main/events.html",context={"admin": Organization.objects.get(organization_abbrv='UPESC')})
#def create_addendum(request):
def participatingevents(request):
    username = request.user.get_username()
    print(username)
    match_participant = Participant.objects.filter(Q(representative__organization__organization_abbrv__icontains=username))
    #print(match_participant)
    #my_events = Event.objects.filter(Q(event_name=match_participant__event_name))
    return render(request = request,
                  template_name="main/participatingevents.html",
                  context={"participants": match_participant, "events":match_participant.order_by('event_name').distinct('event_name'),"admin": Organization.objects.get(organization_abbrv='UPESC')})
class EventDetailView(DetailView):

    model = Event   
    def get_context_data(self, *args, **kwargs):
        context = super(EventDetailView, self).get_context_data(*args, **kwargs)
        context['admin']= Organization.objects.get(organization_abbrv='UPESC')
        context['activities'] = Activity.objects.filter(event_name=Event.objects.get(event_name=self.object.event_name))
        return context
class AdminEventDetailView(DetailView):
    model = Event   
    template_name = 'main/adminevent_detail.html'
    def get_context_data(self, *args, **kwargs):
        form = UpdateEventForm(self.request.POST)
        context = super(AdminEventDetailView, self).get_context_data(*args, **kwargs)
        context['admin']= Organization.objects.get(organization_abbrv='UPESC')
        context['form'] = form
        self.request.session['admin_previous_event'] = self.object.event_name
        return context
class MyEventDetailView(DetailView):
    model = Event
    def get_context_data(self, *args, **kwargs):
        #tempvar = {'event' : self.object.event_name}
        tempvar = self.object.event_name
        self.request.session['previous_view'] = tempvar
        print('event detail: ',self.request.session['previous_view'])
        context = super(MyEventDetailView, self).get_context_data(*args, **kwargs)
        #context['participants'] =Participant.objects.all()
        participants = Participant.objects.filter(event_name__event_name__icontains=self.object.event_name)
        temp = Participant.objects.filter(event_name__event_name__icontains=self.object.event_name).values('representative')
        temp1 = Student.objects.filter(pk__in=temp).values('organization')
        context['participants'] = participants
        context['organization'] = Organization.objects.filter(organization_abbrv__in=temp1)
        context['addendum'] = Addendum.objects.filter(event_name__event_name__icontains=self.object.event_name)
        context['addendum_approved'] = Addendum.objects.filter(signature_list_id__signature=True).filter(event_name__event_name__icontains=self.object.event_name)
        #context['consensus'] = Consensus.objects.filter(signature_list_id__isnull=True).filter(event_name__event_name__icontains=self.object.event_name)
        context['consensus'] = Consensus.objects.filter(event_name=self.object.event_name)
        context['admin'] = Organization.objects.get(organization_abbrv='UPESC')
        context['activities'] = Activity.objects.filter(event_name=Event.objects.get(event_name=self.object.event_name))
        #print(participants)
        return context
class MyEventParticipantDetailView(DetailView):
    model = Participant
    def get_context_data(self, *args, **kwargs):
        tempvar = self.object.event_name.event_name
        self.request.session['previous_view_participating_event'] = tempvar
        representative = self.object.representative.student_number
        self.request.session['previous_view_representative'] = representative
        tempvar = self.object.representative.organization.organization_abbrv
        self.request.session['previous_view_organization'] =tempvar
        context = super(MyEventParticipantDetailView, self).get_context_data(*args, **kwargs)
        participants = Participant.objects.filter(representative__student_number__icontains=self.object.representative.student_number).filter(event_name__event_name__icontains=self.object.event_name)
        context['participants'] = participants
        context['students'] = Student.objects.filter(organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()))
        return context
    pass
class MyEventCreateAddendum(CreateView):
    template_name = 'main/addendum_form.html'
    model = Addendum
    form_class = NewAddendumForm
    queryset = Addendum.objects.all()
    #fields = ['event_name','addendum_revision','addendum_reason']
    def get_success_url(self):
        return '/myevents/'

    def form_valid(self,form):
        prev_event_name = self.request.session.get('previous_view', None)
        print(prev_event_name)
        form.instance.event_name = Event.objects.get(event_name =prev_event_name)
        print(form.cleaned_data)
        return super().form_valid(form)
class MyEventCreateConsensus(CreateView):
    template_name = 'main/consensus_form.html'
    model = Consensus
    form_class = NewConsensusForm
    queryset = Consensus.objects.all()
    def get_success_url(self):
        return '/myevents/'
    def get_context_data(self, *args, **kwargs):
        context = super(MyEventCreateConsensus, self).get_context_data(*args, **kwargs)
        context['students'] = Student.objects.filter(organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()))
        return context
    def form_valid(self,form):
        organization = self.request.user.get_username()
        prev_event_name = self.request.session.get('previous_view', None)
        print(prev_event_name)
        form.instance.event_name = Event.objects.get(event_name =prev_event_name)
        students_from_org = Student.objects.filter(organization__organization_abbrv = organization)
        print(students_from_org)
        representative = form.cleaned_data['representative']
        form.instance.representative = Student.objects.get(Q(student_number=representative) & Q(organization__organization_abbrv=organization))
        temp = Signatures.objects.create(signature=True, representative = Student.objects.get(student_number=representative, organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()) ))
        form.instance.signature_list_id = temp
        print(form.cleaned_data)
        return super().form_valid(form)
        
class ParticipatingEventCreateConsensus(CreateView):
    template_name = 'main/consensus_form.html'
    model = Consensus
    form_class = NewConsensusForm
    queryset = Consensus.objects.all()
    def get_success_url(self):
        return '/myevents/'
    def get_context_data(self, *args, **kwargs):
        context = super(ParticipatingEventCreateConsensus, self).get_context_data(*args, **kwargs)
        context['students'] = Student.objects.filter(organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()))
        return context
    def form_valid(self,form):
        organization = self.request.user.get_username()
        prev_event_name = self.request.session.get('previous_event', None)
        form.instance.event_name = Event.objects.get(event_name =prev_event_name)

        #students_from_org = Student.objects.filter(organization__organization_abbrv = organization)
        representative = form.cleaned_data['representative']
        
        temp=Signatures.objects.create(signature=True, representative = Student.objects.get(student_number=representative, organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()) ))
        form.instance.signature_list_id = temp
        form.instance.representative = Student.objects.get(Q(student_number=representative) & Q(organization__organization_abbrv=organization))

        return super().form_valid(form)

class ParticipatingEventDetailView(DetailView):
    model = Event
    template_name = 'main/participatingevents-detail.html'
    def get_context_data(self, *args, **kwargs):
        #tempvar = {'event' : self.object.event_name}
        context = super(ParticipatingEventDetailView, self).get_context_data(*args, **kwargs)

        username = self.request.user.get_username()
        tempvar = self.object.event_name
        self.request.session['previous_event'] = tempvar
        #context['participants'] =Participant.objects.all()
        participants = Participant.objects.filter(representative__organization__organization_abbrv__icontains=username).filter(event_name__event_name=self.object.event_name)
        temp = Participant.objects.filter(event_name__event_name__icontains=self.object.event_name).values('representative')
        temp1 = Student.objects.filter(pk__in=temp).values('organization')
        context['participants'] = participants
        context['organization'] = Organization.objects.get(organization_abbrv=username)
        context['addendum'] = Addendum.objects.filter(signature_list_id__signature=False).filter(event_name__event_name__icontains=self.object.event_name)
        #context['consensus'] = Consensus.objects.filter(signature_list_id__isnull=True).filter(event_name__event_name__icontains=self.object.event_name)
        context['consensus'] = Consensus.objects.filter(event_name__event_name=self.object.event_name).order_by('consensus_revision')
        context['admin'] = Organization.objects.get(organization_abbrv='UPESC')

        #print(participants)
        return context
class ConsensusDetailView(DetailView):
    model = Consensus
    def get_context_data(self, *args, **kwargs):
        tempvar = self.object.signature_list_id.list_id
        self.request.session['consensus_sig_id'] = tempvar
        tempvar = self.object.id
        self.request.session['consensus_id'] = tempvar
        event_name = self.request.session.get('previous_event',None)
        opened_consensus = self.object.representative.student_number
        opened_consensus_org = self.object.representative.organization.organization_abbrv
        print('Hosting Organization:', opened_consensus_org)
        self.request.session['opened_consensus'] = opened_consensus
        self.request.session['opened_consensus_org'] = opened_consensus_org

        context = super(ConsensusDetailView, self).get_context_data(*args, **kwargs)
        context['admin'] = Organization.objects.get(organization_abbrv='UPESC')
        context['students'] = Student.objects.filter(organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()))
        context['participants'] = Participant.objects.filter(event_name = Event.objects.get(event_name=event_name)).distinct('representative')
        context['approved'] = Consensus.objects.filter(consensus_revision=self.object.consensus_revision,consensus_reason=self.object.consensus_reason)
        #print(Consensus.objects.filter(consensus_revision=self.object.consensus_revision,consensus_reason=self.object.consensus_reason).count())
        return context
    pass
class AddendumDetailView(DetailView):
    model = Addendum
    def get_context_data(self, *args, **kwargs):
        tempvar = self.object.signature_list_id.list_id
        self.request.session['addendum_id'] = tempvar
        context = super(AddendumDetailView, self).get_context_data(*args, **kwargs)
        context['admin'] = Organization.objects.get(organization_abbrv='UPESC')
        context['students'] = Student.objects.filter(organization=Organization.objects.get(organization_abbrv=self.request.user.get_username()))
        return context
    pass

def join_event(request):
    return render(request, "main/join-event.html",context = { 'students':Student.objects.filter(organization__organization_abbrv = request.user.get_username())})

def join_event_form_submission(request):
    username = request.user.get_username()
    event_name = request.POST["event_name"]
    representative = request.POST["representative"]
    dirty_players = request.POST["players"]
    num_representatives = dirty_players.count(':')
    
    students = []
    roles = []
    prev_end = 0
    print('representative: ', representative)

    #parses the input from user to be able to insert values to the database
    for x in range(len(dirty_players)):
        if dirty_players[x] == ':' and prev_end == 0:
            students.append(dirty_players[ :x])
            prev_end = x
        elif dirty_players[x] == ':' and x != 0:
            students.append(dirty_players[prev_end+1 :x])
            prev_end = x
        elif dirty_players[x] == ',':
            roles.append(dirty_players[prev_end+1:x])
            prev_end = x
        if dirty_players[x] == ':' and (num_representatives == len(students)):
            roles.append(dirty_players[prev_end+1:len(dirty_players)])

    for n in range(num_representatives):
        Participant.objects.create(event_name=Event.objects.get(event_name=event_name),representative=Student.objects.get(organization=Organization.objects.get(organization_abbrv=username),student_number=representative ),player=Student.objects.get(organization=Organization.objects.get(organization_abbrv=username),student_number=students[n]), role=roles[n] )

    return render(request,"main/join-event.html")
def approve_registration(request):
    username = request.user.get_username()
    authenticator = request.POST["representative"]
    representative = request.session.get('previous_view_representative',None)
    event_name = request.session.get('previous_view_participating_event', None)
    participants = Participant.objects.filter(representative__student_number=representative, event_name__event_name=event_name).values('signature_list_id')
    for entry in participants:
        id = entry['signature_list_id']
    Signatures.objects.filter(list_id = id).update(signature=True)
    Signatures.objects.filter(list_id = id).update(representative = Student.objects.get(student_number=authenticator,organization=Organization.objects.get(organization_abbrv=username)) )

    return redirect("main:homepage")
def admin_addendum(request):
    return render(request,"main/adminaddendum.html", context = {'addendum_pending': Addendum.objects.filter(signature_list_id__signature=False),
                                                                'addendum_approved': Addendum.objects.filter(signature_list_id__signature=True),
                                                                'organization':Organization.objects.all(),
                                                                "admin": Organization.objects.get(organization_abbrv='UPESC'),
                                                                "event":Event.objects.all()})
def approve_addendum(request):
    username = request.user.get_username()
    authenticator = request.POST["representative"]
    addendum_id = request.session.get('addendum_id',None)
    print(addendum_id)
    Signatures.objects.filter(list_id = addendum_id).update(signature=True)
    Signatures.objects.filter(list_id = addendum_id).update(representative = Student.objects.get(student_number=authenticator,organization=Organization.objects.get(organization_abbrv=username)) )

    return redirect("main:homepage")

#creates new consensus entry with same details as the referenced consensus to create more signature fields
def approve_consensus(request):
    username = request.user.get_username()
    authenticator = request.POST["representative"]
    opened_consensus = request.session.get('opened_consensus',None)
    opened_consensus_org = request.session.get('opened_consensus_org',None)
    print(opened_consensus_org)
    consensus_sig_id = request.session.get('consensus_sig_id',None)
    consensus_id = request.session.get('consensus_id',None)
    #print(consensus_id)
    new_sig=Signatures.objects.create(signature=True,representative=Student.objects.get(student_number=authenticator,organization=Organization.objects.get(organization_abbrv=username)))
    active_consensus = Consensus.objects.get(id=consensus_id)
    
    new=Consensus.objects.create(event_name=Event.objects.get(event_name=active_consensus.event_name),consensus_revision=active_consensus.consensus_revision,consensus_reason=active_consensus.consensus_reason,representative=Student.objects.get(student_number=opened_consensus,organization=Organization.objects.get(organization_abbrv=opened_consensus_org)),signature_list_id=new_sig)
    print('consensus_status: ',Consensus.objects.filter(consensus_revision=active_consensus.consensus_revision,consensus_reason=active_consensus.consensus_reason).exclude(representative__organization__organization_abbrv=active_consensus.event_name.student_representative.organization.organization_abbrv).count(),'/',Participant.objects.filter(event_name=active_consensus.event_name).distinct('representative').count())
    if Consensus.objects.filter(consensus_revision=active_consensus.consensus_revision,consensus_reason=active_consensus.consensus_reason).exclude(signature_list_id__representative__organization__organization_abbrv=active_consensus.event_name.student_representative.organization.organization_abbrv).count() == (Participant.objects.filter(event_name=active_consensus.event_name).distinct('representative').count()):
        now=datetime.now()
        date_time = now.strftime("%m/%d/%Y")
        Consensus.objects.filter(consensus_revision=active_consensus.consensus_revision,consensus_reason=active_consensus.consensus_reason).update(consensus_revision=active_consensus.consensus_revision+' (APPROVED as of: '+date_time+')')
        print("Consensus Completed")

    return redirect("main:homepage")
def remove_registration(request):
    #authenticator = request.POST["representative"]
    representative = request.session.get('previous_view_representative',None)
    event_name = request.session.get('previous_view_participating_event', None)
    organization = request.session.get('previous_view_organization', None)
    Participant.objects.filter(representative=Student.objects.get(student_number=representative, organization=Organization.objects.get(organization_abbrv=organization))).delete()

    return redirect("main:homepage")
def update_event_list(request):
    return render(request,'main/allevents.html',context = {'events':Event.objects.all(),"admin": Organization.objects.get(organization_abbrv='UPESC')})
def update_event(request):
    return render(request,'main/event_form.html', context = {'form': form})
def update_event_submission(request):
    revised_text = request.POST["rules"]
    event_name = request.session.get('admin_previous_event',None)
    Event.objects.filter(event_name=event_name).update(event_rules=revised_text)

    return  redirect("main:homepage")
def database(request):

    return render(request,"main/database.html",
                     {"students": Student.objects.all,
                      "organization": Organization.objects.all,
                      "signatures": Signatures.objects.all,
                      "object": Event.objects.all,
                      "activities": Activity.objects.all,
                      "participants": Participant.objects.all,
                      "addendums": Addendum.objects.all,
                      "consensus": Consensus.objects.all,
                      "admin": Organization.objects.get(organization_abbrv='UPESC')
                     })
                  
