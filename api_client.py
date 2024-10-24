import requests
from bs4 import BeautifulSoup

class SurveyManager:
    def __init__(self):
        self.session = requests.Session()
        self.survey_url = None

    def create_survey_link(self, customer_id, auth_token):
        # create survey url
        url = "https://gqa.api.gdev.exponea.com/data/v2/projects/6f521150-d92d-11ed-a284-de49e5a76b0b/customers/export-one"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        body = {
            "customer_ids": {
                "registered": customer_id
            }
        }

        response = self.session.post(url, json=body, headers=headers)
        response.raise_for_status()

        json_response = response.json()
        self.survey_url = json_response['properties']['survey link']
        return self.survey_url

    def fetch_csrf_token(self, form_url):
        #Get csrf token
        response = self.session.get(form_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')
        return csrf_token

    def submit_survey(self, csrf_token, survey_data, cookie):
        # submit survey
        headers = {
            "Cookie": f"session={cookie}"
        }
        survey_data['csrf_token'] = csrf_token

        response = self.session.post(self.survey_url, data=survey_data, headers=headers)
        return response

    def retrieve_survey_events(self, customer_id, auth_token):
        # get survey json response - for parsing
        url = "https://gqa.api.gdev.exponea.com/data/v2/projects/6f521150-d92d-11ed-a284-de49e5a76b0b/customers/export-one"
        headers = {
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        body = {
            "customer_ids": {
                "registered": customer_id
            }
        }

        response = self.session.post(url, json=body, headers=headers)
        response.raise_for_status()

        return response.json()  
