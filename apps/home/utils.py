from fhirclient import client


@staticmethod
def create_smart_client():
    # Init FHIR Server
    settings = {
        'app_id': 'IRIS_LOCAL_SERVER',
        'api_base': 'http://localhost:52773/csp/healthshare/fhirserveriris/fhir/r4'
    }
    smart = client.FHIRClient(settings=settings)
    return smart


@staticmethod
def create_appointments_from_encounters():
    print('inside utils.load_appointments()')
    import os
    import pathlib
    from fhir.resources.bundle import Bundle
    from fhir.resources.appointment import Appointment

    smart = create_smart_client()

    # print(f'dir = {os.getcwd()}')
    filename = pathlib.Path('apps\home\Cory323_Spinka232_af8ad8f0-c777-3d64-675d-c523555858f2.json')
    patient_bundle = Bundle.parse_file(filename)
    print(f'resource_type = {patient_bundle.resource_type}, ')

    # TODO: Creating appointment using Encounters
    # load JSON file with Encounters
    # For each Encounter
    n = 1
    i = 1
    #   create appointment from Enc

    for res in patient_bundle.entry:

        if i < 100:
            print(f"res {i}, res.resource.resource_type={res.resource.resource_type} ************************************")
            # print(f'res.resource = {res.resource}')
            # for key, value in res.resource

        if res.resource.resource_type == "Encounter":
            enc = res.resource
            n += 1
            # check if Enc is an emergency vitis: jump to next cycle (no need to create appointments for emergency visits)
            # print(enc.classHistory[0].class)
            if enc.classHistory is not None:
                if enc.classHistory[0].class_fhir == 'emergency':
                    continue

            #  check if an appointment exists for the current Encounter
            import fhirclient.models.appointment as app
            print(f'enc.id = {res.resource.id}')
            rows = app.Appointment.where(struct={'id': res.resource.id}).perform_resources(smart.server)
            if len(rows) == 0:
                app = Appointment.construct()
                # assign mandatory properties

                print(f"Appointment with ID : {res.resource.id} not found.")


        #       For each Reference/link

        #           Call reference search link -> get ID
        #               if ref not found -> skip to next appointment
        #           Build a new Reference/link using Reference/ID
        #           Replace with new Ref link

        #       Mappings:
        #           mappings (Appnt = Enc):
        #               id = id
                app.id = enc.id
        #               identifier = identifier
                app.identifier = enc.identifier
        #               text = text (TODO: add generated text later)
        #                   html: Appointment on 1995-05-09 01:35 to 02:20
        #                   html: Appointment on <START> to <END>
        #               status = "arrived"
        #                   serviceCategory = type.0.coding ?
        #                   serviceType = type
        #                   specialty = ?
        #               appointmentType = class ?
        #               reasonReference = reasonReference OR diagnosis.condition.reference Ref/Condition
        #               priority = priority
        #               description = type.0.text
        #               start = DT period.start
        #               end = DT period.end
        #               created = DT system date
        #                   comment = ?
        #                   basedOn = basedOn Ref/ServiceRequest
        #               participant =
        #                   Patient = subject
        #                   Practitioner =
        #                       participant.individual.reference
        #                       participant.type.coding[http://terminology.hl7.org/CodeSystem/v3-ParticipationType|PPRF]
        #                   Location = location[0].location.reference
        #                   Get HealthcareService from Organization (serviceProvider.reference)
        #           save appointment
        #
        #           modify Encounter with new appointment reference.
        #               enc.appointment = Reference / new Appointment

        i += 1
        # End For

    print(f'{n} encounters found.')
    return 1