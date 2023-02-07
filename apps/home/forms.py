from django.forms import ModelForm
from django import forms
# import fhirclient.models.appointment as app
# from apps.home.models import FhirAppointment
from fhir.resources.appointment import Appointment
# from models import FhirAppointment


# class FhirAppointmentForm(ModelForm, FhirAppointment):
# class FhirAppointmentForm(ModelForm):
    # def __init__(self, *args, **kwargs):
    #     forms.ModelForm.__init__(self, *args, **kwargs)  # Call the constructor of ModelForm
    #     FhirAppointment.__init__(self, *args, **kwargs)  # Call the constructor of appointment

    # class Meta:
    #     # import fhirclient.models.appointment as app
    #     # model = Appointment
    #     model = FhirAppointment
    #     fields = "__all__"
        # fields = ['ihi_number', 'appointmentType', 'basedOn', 'cancelationReason']
        # exclude = ('supportingInformation',)
        # widgets = {
        #     'priorRegistrations': forms.TextInput(attrs={'data-role': 'tagsinput'}),
        #     'address': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        #     #'dateOfAttestation' : forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'})),
        # }