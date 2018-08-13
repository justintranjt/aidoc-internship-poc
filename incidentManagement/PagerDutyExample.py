# import statements
from os.path import dirname, join
from pprint import pprint
import pypd
from pypd.errors import BadRequest

# set the from_email to an appropriate email for the api key used
pypd.api_key = 'WyRLzYzEqE2JVmYayKQs'
from_email = 'justin.tran@aidoc.com'

# in this case assuming that there is already a service created
service = pypd.Service.find_one()

# assuming an escalation policy exists as well
escalation_policy = pypd.EscalationPolicy.find_one()

# set some incident data with a incident_key we can use to find it later if
# we want to avoid duplicating until we act on any open incidents
data = {
    'type': 'incident',
    'title': 'incident_demo_incident2',
    'service': {
        'id': service['id'],
        'type': 'service_reference',
    },
    'priority': {
        'id': 'PS5668',
        'type': 'priority',
        'summary': 'P3'
    },
    'incident_key': 'incident_demo_key',
    'body': {
        'type': 'incident_body',
        'details': 'A GPU is being throttled after continuously hitting 100% usage. Reset the GPU and check for scheduled tasks taking up cycles.',
    },
    'escalation_policy': {
        'id': escalation_policy['id'],
        'type': 'escalation_policy_reference',
    }
}

# if the incident is already open it will error with BadRequest
try:
    incident = pypd.Incident.create(
        data=data,
        add_headers={'from': from_email, },
    )
except BadRequest:
    incident = pypd.Incident.find(incident_key='incident_demo_key')[-1]

# mergable incident
data_mergable = data.copy()
mergable_key = 'incident_demo_key_mergable'
data_mergable['incident_key'] = mergable_key

try:
    to_merge = pypd.Incident.create(
        data=data_mergable,
        add_headers={'from': from_email, }
    )
except BadRequest:
    to_merge = pypd.Incident.find(incident_key=mergable_key)[-1]

# ack it, snooze it, resolve it?
pprint(incident)
pprint(incident.json)
incident.acknowledge(from_email)
incident.snooze(from_email, duration=3600)
incident.create_note(from_email, 'This is a note!')
incident.merge(from_email, [to_merge, ])

# before we trigger an event get all currently triggered incidents
triggered_incidents = pypd.Incident.find(statuses=['triggered', ])

# let's see if events and alerts work! This would be for a custom integration
pypd.EventV2.create(data={
    'routing_key': '5ee282116199453bbdbecb82e77a8050',
    'event_action': 'trigger',
    'payload': {
        'summary': 'this is an error event!',
        'severity': 'error',
        'source': 'pypd bot',
    }
})

# wait for our events to trigger incidents
incidents = pypd.Incident.find(statuses=['acknowledged', ])

# resolve and finish up
for i in incidents:
    i.resolve(from_email=from_email, resolution='resolved automagically!')
