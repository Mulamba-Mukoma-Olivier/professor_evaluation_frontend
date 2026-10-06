from api.client import api_client, APIClient
from api.auth_api import AuthAPI
from api.professors_api import ProfessorsAPI
from api.courses_api import CoursesAPI
from api.criteria_api import CriteriaAPI
from api.evaluations_api import EvaluationsAPI
from api.results_api import ResultsAPI
from api.eligibility_api import EligibilityAPI

__all__ = [
    "api_client",
    "APIClient",
    "AuthAPI",
    "ProfessorsAPI",
    "CoursesAPI",
    "CriteriaAPI",
    "EvaluationsAPI",
    "ResultsAPI",
    "EligibilityAPI",
]
