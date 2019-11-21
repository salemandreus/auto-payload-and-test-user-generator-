import requests
import json
from abc import ABCMeta, abstractmethod
from random import randrange

#This module is currently demonstrated to support:
    # post api/endusers/             # Create end users
    # post api/company-manager/     # Create agents
# as these: -return whether fields are required
#  have fields which require randomized unique values conforming to validation rules

# auto data generation is not feasible for creating certain items like campaigns, which requires a lot of static data with no validation rules, but which still is not marked "required" and some field types from the API are mislabeled as string types instead of exposing the field type required, therefore the current generator can't detect it
# Todo: A good halfway point for accommodating this would be a test that DETECTS new model changes from the hardcoded test fixture data and posts a warning when certain fields are not tested in the payload without necessarily GENERATING the data itself - it can use a fixture for the payload creation

# Important Warning: Never implement authtoken as headers for live environment tokens!
    # Current issue reading auth in requests therefore user token is passed into headers
    # for TESTING purposes only, on local environments!
    # Don't expose sensitive data like API keys outside of testing on non-production environments!

class GenerateValidatedCredentials():
    """Gets randomised user credentials that pass validation rules, to apply to selected fields where the need for this validated data is detected"""
    def __init__(self):
        self.random_user = self.generate_random_user()

    def generate_random_user(self):
        """Gets the randomised user credentials that pass validation rules"""
        random_user_raw = requests.get('https://randomuser.me/api/?nat=gb')     # A current constraint of the system we are testing is it cannot handle non-latin characters.
        random_user = json.loads(random_user_raw.content)[u'results'][0]        #Todo: update test data randomiser for this once this known constraint has been fixed
        return random_user

class GenerateRestPayload(GenerateValidatedCredentials):
    """ The calling class
        - first gets randomised user credentials that pass validation rules.
        - then it attempts two different methods to create a body for POST requests -
            it first attempts an Options call and populates the required fields for the body from there
            if Options call is not supported it attempts to populate the required fields based on the returned errors on fields from a rejected POST without a body.
             if no required fields are listed it returns an empty object. """

    def __init__(self, authtoken, method, url):
        GenerateValidatedCredentials.__init__(self)

        try:
            self.payload = GenerateRestPayloadFromOptions({'Authorization': 'Token {}'.format(authtoken)}, method,url, self.random_user).payload
        except KeyError:
            self.payload = GenerateRestPayloadFromRejected({'Authorization': 'Token {}'.format(authtoken)}, method,url, self.random_user).payload


class BaseGenerateRestPayload():
    __metaclass__ = ABCMeta
    """The abstract base class from which shared functionality is inherited by the specific payload generators"""

    @abstractmethod
    def get_method_fields(self, authtoken, method, url):
        """Override with function for getting the method fields for the rest call body"""
        pass

    @abstractmethod
    def create_payload(self, obj, random_user):
        """ Override with function for populating the rest call body dependent on the format of the information received from overridden get_method_fields """
        pass

    def create_field_value(self, key, type, random_user):
        """ Creates the values for the body of the POST request based on the keys of fields applying validation rules, and by the type if no recognised key is specified. """

        # Todo: Make this more efficient - currently is utilised only small-scale requests specifically for creating user accounts for automated test runs and populating only required fields but can be expanded to handle richer data and more complex queries

        # Todo: switch to utilising types instead of key names once our API types are standardised.
        field = ""
        if key.lower() == "cell":  # Applies to end users
            field = '0' + str(randrange(600000000,
                                        899999999))  # Note: Switched to a local random number format because of issues handling some international conversion formats. Randomised phone numbers from the randomiser API are not all south african or consistent length/format, - this ensures consistent number format
            #field = random_user['cell']               # Todo: re-enable once the API bug handling international numbers is fixed.
        elif key.lower() == "email":    # Applies to agents
            field = random_user['email']

        # elif key.lower() == "web_address":        # Todo: Add support for websites
        #     field = random_user['website']

        elif type == 'string' or not type:  # Attempts to generate string if no supported field type specified
            try:
                field = 'autotest'  # using this convention instead of generating unique name/surname for our test data as we are not testing naming character validation here, and to make it easy to search test data and script cleanup automation of only autogenerated test data Todo: testing on randomised user names creation that passes character validation rules once non-latin characters are supported
            except (KeyError):
                raise Exception(
                    "Specialised field type for field {} is not catered for in field data auto-generator. The type for this field was either described in REST Options as a string or no type information was included, but due to its validation requirements cannot be autogenerated as a string - a special case for this field name may need to be added if it utilises validation rules.".format(
                        "\'" + key.upper() + "\'"))
                # general exception is fine in this particular case because tests are supposed to break here if proper test data can't be generated
                # Todo : refine exception message
                # raise Exception("Cannot autogenerate test data for string field: {}. This field was read as a string to be autogenerated with no special validation requirements.".format("\'" + field_definition['label'] + "\'"))
        if field == "":
            raise Exception("Required field type {} for field {} was not catered for in the payload generator therefore the field could not be populated.".format(
                        "\'" + type.upper() + "\'","\'" + key.upper() + "\'"))
        return field


class GenerateRestPayloadFromOptions(BaseGenerateRestPayload):
    """ Attempts an Options call and populates the required fields for the body of a successful POST to the same URL from there. A key error is thrown if Options is not supported.
 """
    def __init__(self, authtoken, method, url, random_user):
        template = self.get_method_fields(authtoken, method, url)
        self.payload = self.create_payload(template, random_user)

    def get_method_fields(self, authtoken, method, url):
        """ Attempt to create request body from Options if it supports actions for the method. Currently only used on POST methods."""
        response = requests.options(url, headers=authtoken)
        content = json.loads(response.content)
        fields = content['actions'][method.upper()]                                                         # Todo: build support for PUT and other methods

        return fields
        # if generating fields fails the calling function handles this - it will first attempt GenerateRestPayloadFromRejected instead of returning response at this point

    def create_payload(self, obj, random_user):
        """ Populates each field on the object based on the Options call response """
        newObj = {}
        for key in obj:
            if obj[key]['required'] == True:
                if obj[key]['type'] == 'nested object':
                    newObj[key] = self.create_payload((obj[key]['children']))
                else:
                    newObj[key] = self.create_field_value(obj[key]['label'], obj[key]['type'], random_user)
        return newObj


class GenerateRestPayloadFromRejected(BaseGenerateRestPayload):
    """ attempts to populate the required fields for the body based on the returned errors on fields from an initial 400 response of a rejected bodiless POST of the request to be populated.
             if no required fields are listed in the 400 response to create a body it returns an empty object."""

    def __init__(self, authtoken, method, url, random_user):
        self.get_method_fields(authtoken, method, url, random_user)


    def get_method_fields(self, authtoken, method, url, random_user):

        # If Options for that method is not supported, send a request with no payload and see what is required from the reject message
        response = getattr(requests, method.lower())(url, headers=authtoken)
        content = json.loads(response.content)

        if (response.status_code == 400): #, "could not detect required payload fields for METHOD: {} at API URL {}".format(self.method.upper(), self.url)
            fields = json.loads(response.content)
            self.payload = self.create_payload(fields, random_user)
        else:
            # This caters for GET requests and requests with optional data, which is currently not supported in the automated payload detector for scope reasons, as well as for being able to test scenarios where unauthorized/forbidden should be returned independently of whether a payload was successfully generated
            self.payload = {}


    def create_payload(self, obj, random_user):
        """ Populates each field on the object based on the required field errors of the initial bodiless POST's 400 response """
        BaseGenerateRestPayload.create_payload(self, obj, random_user)
        newObj = {}
        for key in obj:
            if type(key) == dict:
                # ToDo: Fix
                newObj[key] = self.create_payload(obj[key], random_user)
            else:
                newObj[key] = self.create_field_value(key, "", random_user)
        return newObj
