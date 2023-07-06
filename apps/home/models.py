# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
# import fhirclient.models.appointment as app
from fhir.resources.appointment import Appointment


# Create your models here.
# class FhirAppointment(models.Model, Appointment):
    # def __init__(self, *args, **kwargs):
    #     models.Model.__init__(self, *args, **kwargs)  # Call the constructor of ModelForm
    #     app.Appointment.__init__(self, *args, **kwargs)  # Call the constructor of appointment

    # ihi_number = models.CharField(max_length=30, blank=True, null=True, verbose_name='IHI No')

    # def __str__(self):
    #     return f'{self.pk} ({self.start})-[{self.end}]'


# class FhirAppointment2(FhirAppointment):
#     class Meta:
#         proxy = True

class SmartClient(models.Model):
        None
