"""
Zoho CRM API Client
Handles authentication and data fetching from Zoho CRM
"""
import os
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class ZohoCRMClient:
    """Client for interacting with Zoho CRM API"""

    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self.accounts_url = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.com")
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.com")
        self.access_token = os.getenv("ZOHO_ACCESS_TOKEN")

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError("Missing required Zoho credentials in .env file")

    def refresh_access_token(self) -> str:
        """
        Get a new access token using the refresh token
        """
        url = f"{self.accounts_url}/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }

        response = requests.post(url, data=data)
        response.raise_for_status()

        token_data = response.json()
        self.access_token = token_data["access_token"]
        return self.access_token

    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        if not self.access_token:
            self.refresh_access_token()

        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}"
        }

    def get_modules(self) -> List[Dict]:
        """
        Get list of all available modules in Zoho CRM
        """
        url = f"{self.api_domain}/crm/v2/settings/modules"

        try:
            response = requests.get(url, headers=self.get_headers())
            response.raise_for_status()
            return response.json().get("modules", [])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expired, refresh and retry
                self.refresh_access_token()
                response = requests.get(url, headers=self.get_headers())
                response.raise_for_status()
                return response.json().get("modules", [])
            raise

    def get_records(
        self,
        module: str,
        page: int = 1,
        per_page: int = 200,
        fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Get records from a specific module

        Args:
            module: Module name (e.g., 'Contacts', 'Accounts')
            page: Page number (starts at 1)
            per_page: Records per page (max 200)
            fields: Specific fields to retrieve (None = all fields)

        Returns:
            Dict with 'data', 'info' keys
        """
        url = f"{self.api_domain}/crm/v2/{module}"

        params = {
            "page": page,
            "per_page": per_page
        }

        if fields:
            params["fields"] = ",".join(fields)

        try:
            response = requests.get(url, headers=self.get_headers(), params=params)

            # Handle empty module (204 No Content)
            if response.status_code == 204:
                return {"data": [], "info": {"more_records": False}}

            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expired, refresh and retry
                self.refresh_access_token()
                response = requests.get(url, headers=self.get_headers(), params=params)

                if response.status_code == 204:
                    return {"data": [], "info": {"more_records": False}}

                response.raise_for_status()
                return response.json()

            # Print detailed error for debugging
            if hasattr(e.response, 'text'):
                print(f"API Error Details: {e.response.text}")

            raise

    def get_all_records(self, module: str) -> List[Dict]:
        """
        Get all records from a module (handles pagination automatically)

        Args:
            module: Module name (e.g., 'Contacts', 'Accounts')

        Returns:
            List of all records
        """
        all_records = []
        page = 1
        has_more = True

        print(f"Fetching records from {module}...")

        while has_more:
            try:
                result = self.get_records(module, page=page, per_page=200)
                records = result.get("data", [])

                if records:
                    all_records.extend(records)
                    print(f"  Fetched page {page}: {len(records)} records (total: {len(all_records)})")
                    page += 1
                else:
                    has_more = False

                # Check if there are more pages
                info = result.get("info", {})
                if not info.get("more_records", False):
                    has_more = False

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 204:
                    # No content - no more records
                    has_more = False
                else:
                    raise

        print(f"✅ Total records fetched: {len(all_records)}")
        return all_records

    def get_field_metadata(self, module: str) -> List[Dict]:
        """
        Get field metadata for a module (field names, types, etc.)
        """
        url = f"{self.api_domain}/crm/v2/settings/fields"
        params = {"module": module}

        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            return response.json().get("fields", [])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                self.refresh_access_token()
                response = requests.get(url, headers=self.get_headers(), params=params)
                response.raise_for_status()
                return response.json().get("fields", [])
            raise
