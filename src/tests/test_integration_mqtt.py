import time

from tests.common import load_data, check_data, unload_data, \
    check_deleted_data, QL_URL_4ORION, QL_URL_4ORION_MQTT, MQTT_TOPIC
from reporter.tests.utils import delete_entity_type
from conftest import *



notify_url = "{}".format(QL_URL_4ORION_MQTT)
mqtt_topic = "{}".format(MQTT_TOPIC)

services = ['t1', 't2']

SLEEP_TIME = 1


def headers(service=None, service_path=None, content_type=True):
    h = {}
    if content_type:
        h['Content-Type'] = 'application/json'
    if service:
        h['Fiware-Service'] = service
    if service_path:
        h['Fiware-ServicePath'] = service_path

    return h


def test_integration_basic():
    entities = []
    try:
        entities = load_data(old=False, entity_type="TestEntity")
        assert len(entities) > 1
        # sleep should not be needed now since we have a retries in
        # check_data...
        time.sleep(10)
        check_data(entities, False)
    finally:
        unload_data(entities)
        check_deleted_data(entities)


def do_integration(entity, subscription, orion_client, service=None,
                   service_path=None):

    try:
        subscription_id = orion_client.subscribe(subscription, service,
                                                 service_path). \
            headers['Location'][18:]
        time.sleep(1)
        orion_client.insert(entity, service, service_path)
        entities_url = "{}/entities".format(QL_URL)

        h = headers(
            content_type=False)
        r = None
        for t in range(30):
            r = requests.get(entities_url, params=None, headers=h)
            if r.status_code == 200:
                break
            else:
                time.sleep(1)
        assert r.status_code == 200
        entities = r.json()
        assert len(entities) == 1

        assert entities[0]['entityId'] == entity['id']
        assert entities[0]['entityType'] == entity['type']
    finally:
        delete_entity_type(service, entity['type'], None)
        orion_client.delete(entity['id'], service, service_path)
        orion_client.delete_subscription(subscription_id, service,
                                         service_path)


@pytest.mark.parametrize("service", services)
def test_integration(service, entity, orion_client):
    """
    Test Reporter using input directly from an Orion notification and output
    directly to Cratedb.
    """
    subscription = {
        "description": "Integration Test subscription",
        "subject": {
            "entities": [
                {
                    "id": entity['id'],
                    "type": "Room"
                }
            ],
            "condition": {
                "attrs": [
                    "temperature",
                ]
            }
        },
        "notification": {
            "mqtt": {
                "url": notify_url,
                "topic": mqtt_topic
            },
            "attrs": [
                "temperature",
            ],
            "metadata": ["dateCreated", "dateModified"]
        },
        "throttling": 1,
    }
    do_integration(entity, subscription, orion_client, service, "/")


@pytest.mark.parametrize("service", services)
def test_air_quality_observed(service, air_quality_observed, orion_client):
    entity = air_quality_observed
    subscription = {
        "description": "Test subscription",
        "subject": {
            "entities": [
                {
                    "id": entity['id'],
                    "type": entity['type']
                }
            ],
            "condition": {
                "attrs": []  # all attributes
            }
        },
        "notification": {
            "mqtt": {
                "url": notify_url,
                "topic": mqtt_topic
            },
            "attrs": [],  # all attributes
            "metadata": ["dateCreated", "dateModified"]
        }
    }
    do_integration(entity, subscription, orion_client, service, "/")

