# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import json
import math

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from fhirclient import client
import logging

from fhirclient.models.fhirabstractbase import FHIRValidationError

# from apps.home.forms import FhirAppointmentForm
# from apps.home.models import FhirAppointment

# from forms import FhirAppointmentForm
# from models import FhirAppointment

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logo_file = ""
server_number = 1
server_url = ''
server_name = ''


@login_required(login_url="/login/")
def index(request):
    global server_number
    server_requested = int(request.GET.get('server', '0'))
    if server_requested != 0:
        server_number = server_requested
    print(f'server_number={server_number}')
    context = {'segment': 'index'}
    context = get_stats(server_number)
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


def create_smart_client(server):
    global logo_file
    global server_number
    global server_url
    global server_name
    # Init FHIR Server
    settings = {}

    # use previously set server number if not given
    if server == 0 or server is None:
        server = server_number
    else:
        server_number = server

    if server_number == 1:
        server_name = 'InterSystems IRIS Local server'
        logo_file = 'IRIS.png'
        settings = {
            'app_id': 'IRIS_LOCAL_SERVER',
            'api_base': 'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4'
        }
    elif server_number == 2:
        server_name = 'InterSystems IRIS Cloud server'
        logo_file = 'IRIS.png'
        settings = {
            'app_id': 'IRIS_CLOUD_SERVER',
            'api_base': 'https://fhir.yxlrtoae.static-test-account.isccloud.io'
        }
    elif server_number == 3:
        server_name = 'HAPI server'
        logo_file = 'Hapi.png'
        settings = {
            'app_id': 'HAPI_CLOUD_SERVER',
            'api_base': 'https://hapi.fhir.org/baseR4'
        }
    elif server_number == 4:
        server_name = 'Firely server'
        logo_file = 'firely.jpg'
        settings = {
            'app_id': 'FIRELY_CLOUD_SERVER',
            'api_base': 'https://server.fire.ly/r4'
        }
    elif server_number == 5:
        server_name = 'Cerner server'
        logo_file = 'cerner.png'
        settings = {
            'app_id': 'CERNER_CLOUD_SERVER',
            'api_base': 'https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d'
        }
    elif server_number == 6:
        server_name = 'EPIC server'
        logo_file = 'Epic.png'
        settings = {
            'app_id': 'EPIC_CLOUD_SERVER',
            'api_base': 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4'
        }

    print(f'create_smart_client - settings={settings}')
    server_url = settings["api_base"]
    smart = client.FHIRClient(settings=settings)
    return smart, server_name


def print_resource(resource, indent=None, length=100):
    s = json.dumps(resource.as_json(), indent=indent)
    print(s[:length-4]+' ...' if len(s)>length else s)


def get_stat_row(resource_name, group_name, stat_number, icon_css):
    row_stat = {}
    row_stat['resource'] = resource_name
    row_stat['group_name'] = group_name
    row_stat['number'] = stat_number
    row_stat['icon'] = icon_css
    if group_name == 'Planning':
        group_color = '#25629fbb'
    elif group_name == 'Base':
        group_color = '#5a5a5abb'
    elif group_name == 'Clinical':
        group_color = '#dc3545bb'
    elif group_name == 'Financial':
        group_color = '#28a745bb'
    row_stat['group_color'] = group_color

    return row_stat


# Get stats from each FHIR Res
def get_resource_stats(res_class, search_cri, smart_server):
    import fhirclient.models.bundle as b
    search_bundle = b.Bundle()
    try:
        return res_class.where(search_cri).perform(smart_server).total

    except FHIRValidationError:
        return 0


def get_common_context():
    global server_name
    global server_url
    context = {
        'server_name': server_name,
        'server_url': server_url,
    }
    return context


# Get Dashboard stats from ALL FHIR Res
def get_stats(server_number):
    # do local imports
    import fhirclient.models.patient as pat
    import fhirclient.models.appointment as app
    import fhirclient.models.slot as slo
    import fhirclient.models.schedule as sch
    import fhirclient.models.practitioner as pra
    import fhirclient.models.location as loc
    import fhirclient.models.organization as org
    import fhirclient.models.healthcareservice as hsv
    import fhirclient.models.encounter as enc
    import fhirclient.models.condition as con
    import fhirclient.models.allergyintolerance as alg
    import fhirclient.models.task as tas
    import fhirclient.models.observation as obs
    import fhirclient.models.procedure as pro
    import fhirclient.models.diagnosticreport as diag
    import fhirclient.models.medicationrequest as mr
    import fhirclient.models.medication as med
    import fhirclient.models.medicationstatement as ms
    import fhirclient.models.servicerequest as sr
    import fhirclient.models.immunization as imm
    import fhirclient.models.claim as cla
    import fhirclient.models.claimresponse as cr
    import fhirclient.models.paymentnotice as pn

    smart, server_name = create_smart_client(server_number)
    context = {}
    error_msg = ''

# 'participant.actor': '13'
    #     _summary=count,

    # appointments    = app.Appointment.where(struct={'_summary': 'count'}).perform_resources(smart.server)
    summary_search = struct={'_summary': 'count'}
    # summary_search  = struct = {}
    # list of FHIR classes
    class_list = [app.Appointment, slo.Slot, sch.Schedule, tas.Task, pat.Patient, pra.Practitioner,
                  # 0-5
                  org.Organization, loc.Location, hsv.HealthcareService, enc.Encounter, con.Condition,
                  # 6-10
                  alg.AllergyIntolerance, pro.Procedure, obs.Observation, diag.DiagnosticReport,
                  # 11-14
                  mr.MedicationRequest, ms.MedicationStatement, sr.ServiceRequest, med.Medication,
                  # 15-18
                  imm.Immunization, cla.Claim, cr.ClaimResponse, pn.PaymentNotice,
                  # 19-22
                  ]
    # response object collection
    count_list = []

    try:
        import time
        start = time.time()
        for fhir_class_obj in class_list:
            count_list.append(get_resource_stats(fhir_class_obj, summary_search, smart.server))
        end = time.time()
        print(f'{len(count_list)} FHIR resources took {math.trunc(end - start)} secs')

        # Construct list of stats into a list of dictionaries
        planning_list = []
        planning_list.append(get_stat_row('Appointments', 'Planning',count_list[0], 'fas fa-calendar-check'))
        planning_list.append(get_stat_row('Slots', 'Planning',count_list[1], 'fas fa-calendar-day'))
        planning_list.append(get_stat_row('Schedules', 'Planning',count_list[2], 'fas fa-calendar-alt'))
        planning_list.append(get_stat_row('Tasks', 'Planning',count_list[3], 'fas fa-tasks'))
        planning_list.append(get_stat_row('Service Requests', 'Planning',count_list[17], 'fas fa-notes-medical'))

        base_list = []
        base_list.append(get_stat_row('Patients', 'Base',count_list[4], 'fas fa-hospital-user'))
        base_list.append(get_stat_row('Practitioners', 'Base',count_list[5], 'fas fa-user-md'))
        base_list.append(get_stat_row('Hospitals', 'Base',count_list[6], 'fas fa-clinic-medical'))
        base_list.append(get_stat_row('Locations', 'Base',count_list[7], 'fas fa-building'))
        base_list.append(get_stat_row('Health. Services', 'Base',count_list[8], 'fas fa-briefcase-medical'))
        base_list.append(get_stat_row('Encounters', 'Base',count_list[9], 'fas fa-briefcase-medical'))

        clinical_list = []
        clinical_list.append(get_stat_row('Conditions', 'Clinical',count_list[10], 'fa fa-user-injured'))
        clinical_list.append(get_stat_row('Allergies', 'Clinical',count_list[11], 'fas fa-allergies'))
        clinical_list.append(get_stat_row('Observations', 'Clinical',count_list[13], 'fas fa-microscope'))
        clinical_list.append(get_stat_row('Procedures', 'Clinical',count_list[12], 'fas fa-procedures'))
        clinical_list.append(get_stat_row('Diag. Reports', 'Clinical',count_list[14], 'fas fa-diagnoses'))
        clinical_list.append(get_stat_row('Medi. Requests', 'Clinical',count_list[15], 'fas fa-prescription-bottle'))
        clinical_list.append(get_stat_row('Medi. Statements', 'Clinical',count_list[16], 'fas fa-file-prescription'))
        clinical_list.append(get_stat_row('Medications', 'Clinical',count_list[18], 'fas fa-capsules'))
        clinical_list.append(get_stat_row('Immunizations', 'Clinical',count_list[19], 'fas fa-syringe'))

        financial_list = []
        financial_list.append(get_stat_row('Claims', 'Financial',count_list[20], 'fas fa-file-invoice-dollar'))
        financial_list.append(get_stat_row('Claim Responses', 'Financial',count_list[21], 'fas fa-receipt'))
        financial_list.append(get_stat_row('Payments', 'Financial',count_list[22], 'far fa-credit-card'))
        # stat_list.append(get_stat_row('', len(), 'fas '))
        # logger.debug(f' len(appointments)={len(appointments)}')
        print(f'logo_file={logo_file}')


        # Get appointment list
        app_doctors = []

        # appointments = appointments.sort()
        last_doc = ""
        #
        # for appointment in appointments:
        #     from datetime import datetime
        #     # print(appointment.as_json())
        #
        #     for participant in appointment.participant:
        #
        #         # print(f'participant.type={participant.actor.reference[0:13]}')
        #         if participant.actor is None:
        #             continue
        #
        #         if participant.actor.reference[0:13] == "Practitioner/":
        #             row = {}
        #             # [e for e in patient_bundle.entry if e.resource.resource_type=='Encounter'][0].resource.subject
        #             # add only unique doctors
        #             if last_doc != participant.actor.display:
        #                 row["doctor"] = participant.actor.display
        #                 last_doc = participant.actor.display
        #             else:
        #                 row["doctor"] = ""
        #
        #             if participant.period is not None:
        #                 row["date"] = participant.period
        #                 print(f'participant.period={participant.period}')
        #             else:
        #                 # row["date"] = datetime.strptime(appointment.start.__str__(), '%y-%m-%dT%H:%M:%S')
        #                 row["date"] = appointment.start.isostring
        #                 print(f'appointment.start={appointment.start.isostring}')
        #             row["status"] = participant.status
        #             row["priority"] = appointment.priority
        #             app_doctors.append(row)

            # print(appointment)

        context = {
            'app_doctors': app_doctors,
            'base_list': base_list,
            'planning_list': planning_list,
            'financial_list': financial_list,
            'clinical_list': clinical_list,
            'server_name:': 'Firely Server',
            'stat_summary': f'{len(count_list)} FHIR resources',
            'refresh_time': round(end - start, 1),
            'server_name':  server_name,
            'logo_file': logo_file,
            'server_url': server_url,
            'error': error_msg,
        }
        # for doc in app_doctors:
        #     print(f'doctors={doc}')

    except FHIRValidationError:
        pass
        # for err in FHIRValidationError.errors:
        #     print(err)
    except ConnectionError:
        k = f'Error connecting to server : {server_name}'
        context = {
            'error': error_msg,
        }
        pass

    return context


def generate_report(request):
    global server_name
    from django.shortcuts import render
    from plotly.offline import plot
    from plotly.graph_objs import Scatter

    # todo: remove server no
    smart, server_name = create_smart_client(4)
    report_name = 'Patient Distribution'
    import fhirclient.models.patient as app
    patients = app.Patient.where(struct={'_elements': 'birthDate', '_count': '100'}).perform_resources(smart.server)
    print(f'count(patients)={len(patients)}, type={type(patients)}, type[0]={type(patients[0])}')
    x_data = []
    y_data = []
    age_dist = {}
    for pat in patients:
        if type(pat) is app.Patient:
            if pat.birthDate is not None:
                birth_year = pat.birthDate.date.year
                if birth_year > 1800:
                    if birth_year in age_dist:
                        age_dist[birth_year] += 1
                    else:
                        age_dist[birth_year] = 1

        # sort the dataset
    # age_dist = sorted(age_dist.items(), key=lambda x:x[1])

    for year in age_dist:
        print(f'year: {year} = {age_dist[year]}')
        x_data.append(year)
        y_data.append(age_dist[year])

    # x_data = [0, 1, 2, 3]
    # y_data = [x ** 2 for x in x_data]

    plot_div = plot([Scatter(x=x_data, y=y_data,
                             mode='lines', name='test',
                             opacity=0.8, marker_color='green')],
                    output_type='div', include_plotlyjs=False)
    context = get_common_context()
    context['report_name'] = report_name
    context['plot_div'] = plot_div
    return render(request, "home/reports-1.html", context=context)


def generate_report2(request):
    global server_name
    from django.shortcuts import render
    import plotly.express as px
    import datetime
    import pandas as pd
    from pandas import json_normalize

    # todo: remove server no
    smart, server_name = create_smart_client(3)
    current_year = datetime.date.today().year
    report_name = 'Patient Distribution'
    import fhirclient.models.patient as app
    patients = app.Patient.where(struct={'_elements': 'birthDate, gender', '_count': '100'}).perform_resources(smart.server)
    # for pat in patients:
    #     if type(pat) is app.Patient:
    #         if pat.birthDate is not None:
    #             pat['birthYear'] = pat.birthDate.date.year
    patient_dict = {"bundle": [pat.as_json() for pat in patients]}
    # print(patient_dict)
    patient_df = json_normalize(patient_dict['bundle'])
    # agg_df = patient_df.agg([])
    fig = px.scatter(patient_df, x="birthYear", y="gender",
                     # color="species",
                     # size='petal_length',
                     # hover_data=['petal_width']
                     )
    # print(df2)

    print(f'count(patients)={len(patients)}, type={type(patients)}, type[0]={type(patients[0])}')
    x_data = []
    y_data = []
    age_dist = {}
    patients_without_bd = 0
    for pat in patients:
        if type(pat) is app.Patient:
            if pat.birthDate is not None:
                birth_year = pat.birthDate.date.year
                if 1900 < birth_year <= current_year:
                    if birth_year in age_dist:
                        age_dist[birth_year] += 1
                    else:
                        age_dist[birth_year] = 1
            else:
                patients_without_bd += 1
        else:
            print(pat)

    print(f'patients without bd={patients_without_bd}')
        # sort the dataset
    # age_dist = sorted(age_dist.items(), key=lambda x:x[1])

    for year in age_dist:
        print(f'year: {year} = {age_dist[year]}')
        x_data.append(year)
        y_data.append(age_dist[year])

    # x_data = [0, 1, 2, 3]
    # y_data = [x ** 2 for x in x_data]

    # fig = px.scatter(
    #     x=x_data,
    #     y=y_data,
    #     # color=[]
    #     size=y_data,
    #     labels={'y': 'No of Patients','x': 'Year born' },
    #     title=f'No of Patients per birth year: (Sample size: {sum(y_data)} patients)'
    # )
    plot_div = fig.to_html()
    context = get_common_context()
    context['report_name'] = report_name
    context['plot_div'] = plot_div
    return render(request, "home/reports-1.html", context=context)


def register_smart_app(request):
    context = {
        'rows': None,
    }
    html_template = loader.get_template('home/register-smart-app.html')
    return HttpResponse(html_template.render(context, request))


def launch_smart_app(request):
    smart_app_launch_url = 'https://psddg3.csb.app/launch'
    # https://launch.smarthealthit.org/v/r4/fhir/.well-known/smart-configuration
    iss = 'https://launch.smarthealthit.org/v/r4/fhir'
    # iss = 'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4',
    launch = 'appContext-1'
    context = {
        'rows': None,
        'smart_app_launch_url': 'https://psddg3.csb.app/launch',
        'iss':  'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4',
        'launch': 'appContext-1'
    }
    # html_template = loader.get_template('home/register-smart-app.html')
    # return HttpResponse(html_template.render(context, request))
    url = f'{smart_app_launch_url}?iss={iss}&launch={launch}'
    print(f'redirect_url = {url}')
    return redirect(url)


def show_report(request, report_no):
    return generate_report2(request)

    smart, server_name = create_smart_client(0)
    import fhirclient.models.appointment as app
    rows = app.Appointment.where(struct={}).perform_resources(smart.server)
    html_template = 'home/reports-1.html'
    context = {
        'rows': rows,
    }
    print(f'report_no={report_no}')
    html_template = loader.get_template(html_template)
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def show_table(request, page_type):

    smart, server_name = create_smart_client(0)
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
    elif page_type == 'CONDITIONS':
        import fhirclient.models.condition as app
        rows = app.Condition.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-conditions.html'
    elif page_type == 'OBSERVATIONS':
        import fhirclient.models.observation as app
        rows = app.Observation.where(struct={}).perform_resources(smart.server)
        html_template = 'home/table-observations.html'

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
    smart, server_name = create_smart_client(0)

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
