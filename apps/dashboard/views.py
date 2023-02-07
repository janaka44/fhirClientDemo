from django.shortcuts import render
from django.http import HttpResponse
from fhirclient import client

# Create your views here.
def showDashboard(request):

    # listCases  = Case.objects.filter(caseType__exact=settings.CaseType.LITIGATION)
    # listDeeds  = NotarialCase.objects.all()
    #

    # util_.addCommonSessionVarsToContext(request, context)

    # Read Patient
    settings = {
        'app_id': 'IRIS_LOCAL_SERVER',
        'api_base': 'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4'
    }
    smart = client.FHIRClient(settings=settings)

    import fhirclient.models.patient as p
    patient = p.Patient.read('3', smart.server)

    context = {
        'full_name': smart.human_name(patient.name[0]),
        'dob': patient.birthDate.isostring,
        'phone': patient.telecom[0].value,
    }
    return HttpResponse(f"Patient: Name={smart.human_name(patient.name[0])}, DOB: {patient.birthDate.isostring}")
    #return render(request, 'dashboard/dashboard.html', context)
