import requests
from datetime import datetime as dt

class StorjNode:
    def __init__(self, name, address, api_port):
        self.name = name
        self.port = api_port
        self.address = address

    def _url(self):
        return f'http://{self.address}:{self.port}/api'

    def _api(self, endpoint):
        '''
        Makes an api call to the Node's Dashboard API and returns the data in json() format.

        Possible endpoints are:
        /sno/
        /sno/satellites
        /sno/satellite/${id}
        /notifications/list?page=1&limit=10
        /notifications/readall
        /notifications/${id}/read

        Payout data is available with v1.3.3
        /heldamount/paystubs/2020-03
        /heldamount/paystubs/2020-02?id=${id}
        '''
        return requests.get(self._url() + endpoint).json()

    def _parse_time(self, time):
        return dt.strptime(time, '%Y-%m-%dT%H:%M:%S.%f')

    def is_available(self):
        try:
           self._api('/sno/')
        except Exception:
           return False
        else:
           return True

    def get_satellite_ids(self):
        return [x['id'] for x in self._api('/sno/')['satellites']]

    def get_id(self):
        return self._api('/sno/')['nodeID']

    def get_disk_used(self):
        return self._api('/sno/')['diskSpace']['used']

    def get_disk_allocated(self):
        return self._api('/sno/')['diskSpace']['available']

    def get_bandwidth(self):
        sat_endpoints = [ '/sno/satellite/' + id for id in self.get_satellite_ids()]
        utilization = self._api('/sno/')['bandwidth']['used']
        egress = 0
        ingress = 0

        for s in sat_endpoints:
            result = self._api(s)
            egress += result['egressSummary']
            ingress += result['ingressSummary']

        return egress, ingress, utilization

    def get_version(self):
        return self._api('/sno/')['version']

    def get_uptime(self):
        return dt.utcnow() - self._parse_time(self._api('/sno/')['startedAt'][:-4])

    def is_updated(self):
        return self._api('/sno/')['upToDate']

    def vetting_progress(self):
        '''
        Calculates the vetting progress of all satellites and returns the
        result as a percentage.
        '''
        sat_endpoints = [ '/sno/satellite/' + id for id in self.get_satellite_ids()]
        successfulAuditsRequired = 100                                                           # The required number of successful audits for a satellite to consider a node as vetted.
        successCounts= []

        for s in sat_endpoints:
            p = self._api(s)['audit']['successCount'] / successfulAuditsRequired
            if p <= 1:
                successCounts.append(p)
            else:
                successCounts.append(1)

        return (sum(successCounts) / len(successCounts)) * 100

    def get_satellites_stats(self):
        connected = 0
        suspended = 0
        disqualified = 0

        for a in self._api('/sno/')['satellites']:
            if a['disqualified'] != None:
                disqualified += 1
            if a['suspended'] != None:
                suspended += 1
            connected += 1

        return connected, suspended, disqualified

    def get_age(self):
        '''
        Calculates the age of the node based on the oldest join date
        out of all the satellites.
        '''
        sat_endpoints = [ '/sno/satellite/' + id for id in self.get_satellite_ids()]
        join_dates = []

        for s in sat_endpoints:
            join_dates.append(self._parse_time(self._api(s)['nodeJoinedAt'][:-4]))

        return dt.utcnow() - sorted(join_dates)[0]
