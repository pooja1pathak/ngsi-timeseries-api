from reporter.httputil import *
from wq.ngsi import FiwareTaskId
from wq.rqutils import find_job_ids_starting_with, load_jobs, delete_jobs


def build_task_id_init_segment():
    fid = FiwareTaskId(fiware_s(), fiware_sp(), fiware_correlator())
    if fiware_correlator():
        return fid.fiware_tags_repr()
    return fid.fiware_svc_and_svc_path_repr()


def list_messages():
    matcher = build_task_id_init_segment()
    job_ids = find_job_ids_starting_with(matcher)
    js = load_jobs(job_ids)
    tasks = [j.args[0] for j in js]
    response_payload = [
        {
            'task-id': t.task_id().id_repr(),
            'fiware-service': t.fiware_service,
            'fiware-service-path': t.fiware_service_path,
            'fiware-correlator': t.fiware_correlator,
            'payload': t.payload
        }
        for t in tasks]
    return response_payload


def delete_messages():
    matcher = build_task_id_init_segment()
    job_ids = find_job_ids_starting_with(matcher)
    delete_jobs(job_ids)