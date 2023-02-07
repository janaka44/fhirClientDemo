# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from fhirclient import client
import logging


# from apps.home.forms import FhirAppointmentForm
# from apps.home.models import FhirAppointment

# from forms import FhirAppointmentForm
# from models import FhirAppointment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


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


def print_resource(resource, indent=None, length=100):
    s = json.dumps(resource.as_json(), indent=indent)
    print(s[:length-4]+' ...' if len(s)>length else s)


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
    import fhirclient.models.encounter as enc
    import fhirclient.models.condition as con

# 'participant.actor': '13'
    #     _summary=count
    # appointments    = app.Appointment.where(struct={'_summary': 'count'}).perform_resources(smart.server)

    appointments    = app.Appointment.where(struct={}).perform_resources(smart.server)
    slots           = slo.Slot.where(struct={}).perform_resources(smart.server)
    schedules       = sch.Schedule.where(struct={}).perform_resources(smart.server)
    patients        = pat.Patient.where(struct={}).perform_resources(smart.server)
    practitioners   = pra.Practitioner.where(struct={}).perform_resources(smart.server)
    organiations    = org.Organization.where(struct={}).perform_resources(smart.server)
    locations       = loc.Location.where(struct={}).perform_resources(smart.server)
    healthcareServices = hsv.HealthcareService.where(struct={}).perform_resources(smart.server)
    encounters      = enc.Encounter.where(struct={}).perform_resources(smart.server)
    conditions      = con.Condition.where(struct={}).perform_resources(smart.server)

    # TODO: remove prints
    app_doctors = []
    logger.debug(f' len(appointments)={ len(appointments)}')
    for appointment in appointments:
        # print(appointment.as_json())
        for participant in appointment.participant:

            # print(f'participant.type={participant.actor.reference[0:13]}')

            if participant.actor.reference[0:13] == "Practitioner/":
                row = {}
                # [e for e in patient_bundle.entry if e.resource.resource_type=='Encounter'][0].resource.subject
                row["doctor"] = participant.actor.display
                if participant.period is not None:
                    row["date"] = participant.period
                    print(f'participant.period={participant.period}')
                else:
                    row["date"] = appointment.start
                    print(f'appointment.start={appointment.start}')
                row["status"] = participant.status
                app_doctors.append(row)

        # print(appointment)

    context = {
        'n_appointments': len(appointments),
        'n_slots': len(slots),
        'n_schedules': len(schedules),
        'n_patients': len(patients),
        'n_practitioners': len(practitioners),
        'n_organiations': len(organiations),
        'n_locations': len(locations),
        'n_healthcareServices': len(healthcareServices),
        'n_conditions': len(conditions),
        'n_encounters': len(encounters),
        'app_doctors': app_doctors
    }
    print(f'doctors={app_doctors[0]}')
    return context


@login_required(login_url="/login/")
def show_table(request, page_type):

    smart = create_smart_client()
    if page_type == 'APPOINTMENTS':
        import fhirclient.models.appointment as app
        rows = app.Appointment.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-appointments.html'
    elif page_type == 'HOSPITALS':
        import fhirclient.models.organization as app
        rows = app.Organization.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-hospitals.html'
    elif page_type == 'HEALTHCARE_SERVICES':
        import fhirclient.models.healthcareservice as app
        rows = app.HealthcareService.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-healthcareServices.html'
    elif page_type == 'PRACTITIONERS':
        import fhirclient.models.practitioner as app
        rows = app.Practitioner.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-practitioners.html'
    elif page_type == 'PATIENTS':
        import fhirclient.models.patient as app
        rows = app.Patient.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-patients.html'

    context = {
        'rows': rows,
    }
    print(f'type of rows={type(rows)}')
    html_template = loader.get_template(html_template)
    return HttpResponse(html_template.render(context, request))


def load_appointments(request):
    # from utils import load_appointments
    # import utils as u

    from apps.home import utils
    utils.create_appointments_from_encounters()
    html_template = loader.get_template('home/table-appointments.html')
    context= {}
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def add_edit_appointment(request):
    from fhir.resources.appointment import Appointment
    import pydantic

    context = {}
    # import fhirclient.models.appointment as app

    pk = 0
    if pk > 0:
        urlAction = 'edit'  # set url to post as Edit
        urlId = f'{pk}/'  # assign pk to edit
    else:
        urlAction = 'add'

    data = dict()
    list_html = ''
    title = 'Add Appointment'
    # url = f'../{urlAction}Appointment/{urlId}'
    url = ''
    listHtmlName = 'AppointmentList.html'
    dtTableHtmlId = '#dtTable-Appointments'
    context = {}
    smart = create_smart_client()

    # rows = app.Appointment.where(struct={}).perform_resources(smart.server)
    # row = FhirAppointment()
    # form = FhirAppointmentForm(request.POST, instance=row)
    form = None
    html_template = loader.get_template('includes/form.html')

    # row = None

    try:
        row = Appointment.construct(status="proposed")
    except pydantic.error_wrappers.ValidationError:
        print(f'Validation Error creating FHIR Object:{type(row)}')
    # row = app.Appointment()

    prop_components = {}
    for prop in row:
        prop_components[prop] = getComponent(prop, row.__annotations__[prop].fhir_type_name())

    context = {
        'props': row.__dict__,
        'props_anno_list': row.__annotations__,
        # 'props': dir(row),
        # 'form': form,
        'title': title,
        # 'pk': pk,
        # 'url': url,
    }
    # data['list_html'] = list_html,
    # data['dtTableHtmlId'] = dtTableHtmlId,
    # data['html_form'] = render_to_string('includes/form.html', context=context, request=request)
    # return JsonResponse(data)
    return HttpResponse(html_template.render(context, request))


def getComponent(field_name, fhirType):
    comp = {}
    if fhirType == 'CodeableConcept':
        pass
    elif fhirType == 'ReferenceType':
        pass
    elif fhirType == '':
        pass

    return comp


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
