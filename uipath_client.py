"""
UiPath Orchestrator API Client
================================
Handles authentication, job triggering, status polling, and result retrieval
via the UiPath Cloud Orchestrator REST API.
"""

import requests
from django.conf import settings


class UiPathClient:
    """
    Client for UiPath Cloud Orchestrator API.

    Usage:
        client = UiPathClient()
        client.authenticate()
        job_key = client.start_job("CompetitorPriceScraper")
        status = client.get_job_status(job_key)
    """

    TOKEN_URL = "https://cloud.uipath.com/identity_/connect/token"

    def __init__(self):
        self.tenant_url = getattr(settings, "UIPATH_TENANT_URL", "")
        self.client_id = getattr(settings, "UIPATH_CLIENT_ID", "")
        self.client_secret = getattr(settings, "UIPATH_CLIENT_SECRET", "")
        self.scope = getattr(settings, "UIPATH_SCOPE", "OR.Jobs OR.Execution")
        self.folder_id = getattr(settings, "UIPATH_FOLDER_ID", 0)
        self.access_token = None

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------
    def authenticate(self):
        """
        Obtain an OAuth2 access token from UiPath Cloud Identity.
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

        try:
            response = requests.post(self.TOKEN_URL, data=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.access_token = data.get("access_token")
            return True
        except requests.RequestException as e:
            print(f"[UiPath Auth Error] {e}")
            return False

    # --------------------------------------------------
    # HEADERS
    # --------------------------------------------------
    def _headers(self):
        """Build request headers with auth token and folder context."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(self.folder_id),
        }

    # --------------------------------------------------
    # GET RELEASE KEY
    # --------------------------------------------------
    def get_release_key(self, process_name):
        """
        Look up the release key for a given process name.
        The release key is required to start a job.
        """
        url = f"{self.tenant_url}/odata/Releases"
        params = {"$filter": f"ProcessKey eq '{process_name}'"}

        try:
            response = requests.get(
                url, headers=self._headers(), params=params, timeout=30
            )
            response.raise_for_status()
            releases = response.json().get("value", [])

            if releases:
                return releases[0].get("Key")
            else:
                print(f"[UiPath] No release found for process: {process_name}")
                return None
        except requests.RequestException as e:
            print(f"[UiPath Release Lookup Error] {e}")
            return None

    # --------------------------------------------------
    # START JOB
    # --------------------------------------------------
    def start_job(self, process_name, input_arguments=None):
        """
        Trigger a UiPath process on the Orchestrator.

        Args:
            process_name: Name of the published process
            input_arguments: Optional dict of input arguments for the bot

        Returns:
            job_key (str) or None on failure
        """
        release_key = self.get_release_key(process_name)
        if not release_key:
            return None

        url = f"{self.tenant_url}/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs"

        payload = {
            "startInfo": {
                "ReleaseKey": release_key,
                "Strategy": "ModernJobsCount",
                "JobsCount": 1,
                "InputArguments": (
                    str(input_arguments) if input_arguments else "{}"
                ),
            }
        }

        try:
            response = requests.post(
                url, headers=self._headers(), json=payload, timeout=30
            )
            response.raise_for_status()
            jobs = response.json().get("value", [])

            if jobs:
                return str(jobs[0].get("Key", ""))
            return None
        except requests.RequestException as e:
            print(f"[UiPath Start Job Error] {e}")
            return None

    # --------------------------------------------------
    # GET JOB STATUS
    # --------------------------------------------------
    def get_job_status(self, job_key):
        """
        Poll the status of a running job.

        Returns:
            dict with keys: state, info, output_arguments
        """
        url = f"{self.tenant_url}/odata/Jobs({job_key})"

        try:
            response = requests.get(url, headers=self._headers(), timeout=30)
            response.raise_for_status()
            data = response.json()

            return {
                "state": data.get("State", "Unknown"),
                "info": data.get("Info", ""),
                "output_arguments": data.get("OutputArguments"),
            }
        except requests.RequestException as e:
            print(f"[UiPath Job Status Error] {e}")
            return {"state": "Error", "info": str(e), "output_arguments": None}

    # --------------------------------------------------
    # GET JOB OUTPUT
    # --------------------------------------------------
    def get_job_output(self, job_key):
        """
        Retrieve the output arguments of a completed job.

        Returns:
            dict of output arguments, or None
        """
        status = self.get_job_status(job_key)
        output = status.get("output_arguments")

        if output and isinstance(output, str):
            import json

            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return {"raw_output": output}
        return output
