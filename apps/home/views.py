# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from fhirclient import client


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    context = get_stats()
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def create_smart_client():
    # Init FHIR Server
    settings = {
        'app_id': 'IRIS_LOCAL_SERVER',
        'api_base': 'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4'
    }
    smart = client.FHIRClient(settings=settings)
    return smart


def get_stats():
    smart = create_smart_client()

    import fhirclient.models.patient as pat
    patient = pat.Patient.read('13', smart.server)
    import fhirclient.models.appointment as app
    import fhirclient.models.slot as slo
    import fhirclient.models.schedule as sch
    import fhirclient.models.practitioner as pra
    import fhirclient.models.location as loc
    import fhirclient.models.organization as org
    import fhirclient.models.healthcareservice as hsv

# 'participant.actor': '13'
    #     _summary=count
    appointments    = app.Appointment.where(struct={' _summary': 'count'}).perform_resources(smart.server)
    slots           = slo.Slot.where(struct={}).perform_resources(smart.server)
    schedules       = sch.Schedule.where(struct={}).perform_resources(smart.server)
    patients        = pat.Patient.where(struct={}).perform_resources(smart.server)
    practitioners   = pra.Practitioner.where(struct={}).perform_resources(smart.server)
    organiations    = org.Organization.where(struct={}).perform_resources(smart.server)
    locations       = loc.Location.where(struct={}).perform_resources(smart.server)
    healthcareServices = hsv.HealthcareService.where(struct={}).perform_resources(smart.server)

    for appointment in appointments:
        appointment.as_json()
        print(appointment)

    context = {
        'n_appointments': len(appointments),
        'n_slots': len(slots),
        'n_schedules': len(schedules),
        'n_patients': len(patients),
        'n_practitioners': len(practitioners),
        'n_organiations': len(organiations),
        'n_locations': len(locations),
        'n_healthcareServices': len(healthcareServices),
    }
    return context


@login_required(login_url="/login/")
def list_appointments(request):
    import fhirclient.models.appointment as app
    smart = create_smart_client()
    appointments = app.Appointment.where(struct={}).perform_resources(smart.server)

    context = {
        'rows': appointments,
    }
    html_template = loader.get_template('home/table.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
