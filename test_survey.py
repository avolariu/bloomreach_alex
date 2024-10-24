import pytest
from api_client import SurveyManager
import time
import re

AUTH_HEADER = "Basic ZmJpaXFsd3dmNWdubnV4bnM3N2ZreGZrb3lzbmw2ZjBuaGYyMXhpeHlreHhzaWlhOWMzNDF4NGV3cjR3MzBuYjpmeXB3ZGx5b2kyc291ODdsdm10bDgwbm1mNjh5Nmh4Zm5naWdzc3VsNjJvanNmMnF4bW5laWFnM3hvNHducGZn"
CUSTOMER_ID = "customer-9d7b59"
FORM_URL = "https://gqa.cdn.gdev.exponea.com/cmp-qa-engineer/s/eyJjdXN0b21lcl9pZCI6IjY2ZmQzM2QzNzA3ODQ4YTExNzBhMmI2ZCIsInN1cnZleV9pZCI6IjY0MzZhNWRiMWMwOWRhNjIxY2RiNDhiMSJ9.aBPOIcj79p9uMDWYBuJ1ZWKQkvE"

@pytest.fixture
def survey_manager():
    return SurveyManager()

def test_successful_submission(survey_manager):

    answers = (
        "Blue",     
        "Jazz",     
        "4",        
        "Test5"     
    )
    
    # Preconditions:

    survey_manager.create_survey_link(CUSTOMER_ID, AUTH_HEADER)
    csrf_token = survey_manager.fetch_csrf_token(FORM_URL)
    cookie = survey_manager.session.cookies.get('session')
    post_data = {
        "question-0": answers[0],
        "question-1": answers[1],
        "question-2": answers[2],
        "question-3": answers[3],
    }

    #Step 1: Submit survey
    response = survey_manager.submit_survey(csrf_token, post_data, cookie)


    #Step 2: Check status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    #Step 3: Check redirection
    assert "/submitted" in response.url, f"Expected '/submitted' in the URL, got {response.url}"

    # Wait for responses to be stored
    time.sleep(15)

    #Step 4: Get survey answers from customer export endpoint
    survey_events = survey_manager.retrieve_survey_events(CUSTOMER_ID, AUTH_HEADER)

    #Step 5: Check last 4 items from events list
    events = survey_events.get("events", [])
    last_4_events = events[-4:]
    
    expected_answers = [
        {"answer": answers[0], "question_id": 0},
        {"answer": [answers[1]], "question_id": 1},
        {"answer": answers[2], "question_id": 2},
        {"answer": answers[3], "question_id": 3},
    ]

    for i, event in enumerate(last_4_events):
        assert event["properties"]["answer"] == expected_answers[i]["answer"], f"Expected answer {expected_answers[i]['answer']}, got {event['properties']['answer']}"
        assert event["properties"]["question_id"] == expected_answers[i]["question_id"], f"Expected question_id {expected_answers[i]['question_id']}, got {event['properties']['question_id']}"



def test_missing_field_submition(survey_manager):

    # Preconditions:
    survey_link = survey_manager.create_survey_link(CUSTOMER_ID, AUTH_HEADER)
    csrf_token = survey_manager.fetch_csrf_token(FORM_URL)
    cookie = survey_manager.session.cookies.get('session')
    post_data = {
        "question-0": "Blue",
        "question-2": "4",
        "question-3": "Test8"
    }

    #Step 1: Submit survey
    response = survey_manager.submit_survey(csrf_token, post_data, cookie)

    #Step 2: Check status code
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    #Step 3: Check that url stays the same
    assert response.url == survey_link, f"Expected URL {survey_link}, but got {response.url}"

    #Step 4: Check the HTML response for error
    html_response = response.text
    print(html_response)
    assert re.search(r'<div class="question-wrapper\s+error">', html_response), "Error message not found"
