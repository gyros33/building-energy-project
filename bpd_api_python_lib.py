#!/usr/bin/env python
"""
BPD API - Python Library
For more information on the BPD API, visit https://sites.google.com/a/lbl.gov/bpd-api-documentation/

Author: Michael Berger
        mberger@lbl.gov
        Lawrence Berkeley National Laboratory
"""
import json
import requests
import os

# Inputs
BPD_URL     = "https://bpd-api.lbl.gov"
USER_NAME   = False  # Replace with API username (string)
API_KEY     = False  # Replace with API key      (string)
HEADERS     = {"Content-Type": "application/json",
               "Authorization": "ApiKey {}:{}".format(USER_NAME, API_KEY)}
TIMEOUT     = {"metadata":{"message":"error",
                           "error":"Timeout error"}}
BADGATE     = {"metadata":{"message":"error",
                           "error":"Bad Gateway"}}

assert USER_NAME and API_KEY, "Please initialize with USER_NAME and API_KEY."

# API Interfacing Functions
def rootquery():
    url      = BPD_URL
    response = requests.get(url=url,
                            data=json.dumps({}),
                            headers=HEADERS,
                            verify=True)
    return "{}\n{}".format(response.json()["message"], url)

def fields(payload=None):
    try:
        if payload != None:
            if payload == {}:
                url      = os.path.join(BPD_URL, "/api/v2/introspection/fields")
                response = requests.get(url)
                return response.json()
            else:
                url      = os.path.join(BPD_URL, "/api/v2/introspection/fields?{}={}".format(payload.keys()[0], payload[payload.keys()[0]]))
                response = requests.get(url)
                return response.json()
        else: print("ERROR: Incorrect inputs to api function.")
    except ValueError: return "Fail: ValueError"

def group_by(payload={}):
    if payload == {}:
        url      = os.path.join(BPD_URL, "/api/v2/introspection/group_by")
        response = requests.get(url)
        return response.json()
    else:
        url      = os.path.join(BPD_URL, "/api/v2/introspection/group_by?{}={}".format(payload.keys()[0], payload[payload.keys()[0]]))
        response = requests.get(url)
        return response.json()

def count(filters={}, recalculate=True):
    url      = os.path.join(BPD_URL, "/api/v2/analyze/count")
    payload  = {"filters": filters,
                "recalculate": recalculate}
    response = requests.post(url=url,
                             data=json.dumps(payload),
                             headers=HEADERS,
                             verify=True)
    return response.json()

def histogram(filters={}, group_by="floor_area", recalculate=True, resolution="high"):
    url      = os.path.join(BPD_URL, "/api/v2/analyze/histogram")
    payload  = {"filters": filters,
                "group_by": group_by,
                "recalculate": recalculate,
                "resolution": resolution}
    response = requests.post(url=url,
                             data=json.dumps(payload),
                             headers=HEADERS,
                             verify=True)

    if response.status_code == 504: return TIMEOUT
    else:                           return response.json()

def scatterplot(filters={}, xaxis="", yaxis="", addfields=[], limit=1000, seed=""):
    url     = urlparse.urljoin(BPD_URL, "/api/v2/analyze/scatterplot")
    payload = {"filters": filters,
               "additional_fields": addfields,
               "limit": limit}

    if yaxis != "": payload["y-axis"] = yaxis
    if seed != "":  payload["seed"] = seed
    if xaxis != "": payload["x-axis"] = xaxis

    response = requests.post(url=url,
                             data=json.dumps(payload),
                             headers=HEADERS,
                             verify=True)

    if response.status_code == 504: return TIMEOUT
    else:                           return response.json()

def table(filters={}, group_by="floor_area", analyze_by="source_eui", recalculate=True):
    url     = urlparse.urljoin(BPD_URL, "/api/v2/analyze/table")
    payload = {"filters": filters,
               "recalculate": recalculate}

    if analyze_by != "": payload["analyze_by"] = analyze_by
    if group_by != "":   payload["group_by"] = group_by

    response = requests.post(url=url,
                             data=json.dumps(payload),
                             headers=HEADERS,
                             verify=True)

    if response.status_code == 504: return TIMEOUT
    else:                           return response.json()

def comparepeergroup(from_filters, to_filters, analyze_by, base={}, method="actuarial", seed=[], recalculate=True):
    url = urlparse.urljoin(BPD_URL, "/api/v2/analyze/compare/peer-group")

    payload = {"from": from_filters,
               "to": to_filters,
               "analyze_by": analyze_by,
               "base": base,
               "method": method,
               "recalculate": recalculate}

    if seed != []: payload["seed"] = seed

    response = requests.post(url=url,
                             data=json.dumps(payload),
                             headers=HEADERS,
                             verify=True)

    if response.status_code == 504:   return TIMEOUT
    elif response.status_code == 502: return BADGATE
    else:                             return response.json()


""" Test """
if __name__ == "__main__":
    # When run, the following code should print:
    # BPD 2.0
    # https://bpd-api.lbl.gov
    # success
    # success
    # success
    # success
    # success
    # success
    # success

    #Note: Remove ["metadata"]["message"] to see full object returned.

    # This block runs the introspective functions.
    print(rootquery())
    print(fields(payload={"field_type":"numerical"})["metadata"]["message"])
    print(group_by(payload={"field_type":"categorical"})["metadata"]["message"])

    # This block runs example queries for a peer group of Commercial buildings in California.
    peer_group = {"state":["CA"], "building_class":["Commercial"]}
    print(count(filters=peer_group)["metadata"]["message"])
    print(histogram(filters=peer_group,
                    group_by=["source_eui"])["metadata"]["message"])
    print(scatterplot(filters=peer_group,
                      xaxis="floor_area",
                      yaxis="source_eui")["metadata"]["message"])
    print(table(filters=peer_group,
                group_by=["facility_type"],
                analyze_by="source_eui")["metadata"]["message"])

    # This block runs an example Regression comparison analysis,
    # comparing commerical buildings in California with VAV control to CAV control.
    peer_group   = {"state":["CA"],
                    "building_class":["Commercial"],
                    "air_flow_control":["Variable Volume","Constant Volume"]}
    compare_from = {"air_flow_control":["Constant Volume"]}
    compare_to   = {"air_flow_control":["Variable Volume"]}
    print(comparepeergroup(from_filters=compare_from,
                           to_filters=compare_to,
                           analyze_by="source_eui",
                           base=peer_group,
                           method="regression")["metadata"]["message"])
