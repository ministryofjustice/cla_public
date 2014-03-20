import urllib
import slumber

from django.conf import settings


API_VERSION = 'v1'
BASE_URI = '{base_uri}/checker/api/{version}'.\
    format(base_uri=settings.BACKEND_BASE_URI, version=API_VERSION)

def get_connection(session=None):
    return slumber.API(BASE_URI, session=session)


connection = slumber.API(BASE_URI)


class FormSerializer(slumber.serialize.JsonSerializer):
    key = "form"
    content_types = ["application/x-www-form-urlencoded", "application/json"]

    def dumps(self, data):
        return urllib.urlencode(data)


def get_auth_connection():
    s = slumber.serialize.Serializer(
        default="form",
        serializers=[
            FormSerializer(),
        ]
    )

    return slumber.API('http://127.0.0.1:8000/', serializer=s)


class Resource(object):
    endpoint_name = None
    endpoint = None
    fields = set()
    required_fields = set()
    connection = None
    pk_name = 'reference'

    def __init__(self, *args):
        if not len(args):
            connection = get_connection()
        else:
            connection = args[0]

        self.connection = connection
        self.endpoint = getattr(self.connection, self.endpoint_name)


    def list(self):
        """
        :return: a list of all objects
        """
        return self.endpoint.get()

    def validate_fields(self, data):
        """
        checks if all required fields have been specified
        """
        keys = set(data.keys())
        if not self.required_fields.issubset(keys):
            missing = ', '.join(self.required_fields.difference(keys))
            raise ValueError(
                'Some required fields not supplied: {missing}'.
                format(missing=missing))

    def update(self, data=None, reference=None, **kwargs):
        """
        :param data: optional, the whole updated object you want to save
        :param kwargs: or, a reference/id for the object to be updated and
        """

        updated = None
        if data is not None and self.pk_name in data:
            # check data has a reference before posting
            self.validate_fields(data)
            updated = self.endpoint.post(data)
            return updated

        if reference:
            updated = self.endpoint(reference).patch(kwargs)

        return updated

    def create(self, data, **kwargs):
        return self.endpoint.post(data)


class Category(Resource):
    endpoint_name = 'category'
    pk_name = 'id'
    fields = {'name', 'description', 'id'}


class EligibilityCheck(Resource):
    fields = {'reference', 'category', 'notes'}

    endpoint_name = 'eligibility_check'

    def create(self, category=None, notes=None):
        """
        begin an eligibility claim
        :param category: id of a category object obtained from
         `get_category_list`
        :param notes: an optional string to be set as the notes field
        :return: the created eligibility claim, including the id
        """

        data = {}
        if category:
            data['category'] = category
            data['notes'] = notes

        return super(EligibilityCheck, self).create(data)


class PersonalDetails(Resource):

    endpoint_name = 'personal_details'

    fields = {'title', 'full_name', 'postcode',
              'street', 'town', 'mobile_phone', 'home_phone'}



    def create(self, title=None, full_name=None, postcode=None,
               street=None, town=None, mobile_phone=None, home_phone=None):

        data = {}

        for f in self.fields:
            data[f] = locals()[f]

        return super(PersonalDetails, self).create(data)

    def validate_fields(self, data):
        super(PersonalDetails, self).validate_fields(data)
        if not 'mobile_phone' or 'home_phone' in data:
            raise ValueError(
                'One of "home_phone" or "mobile_phone" must be supplied.')

class Case(Resource):

    endpoint_name = 'case'

    def create(self, eligibility_check=None, personal_details=None):
        """
        creates a case using a pre-existing pair of an
        eligibility claim object and a personal_details object.
        :param eligibility_check: id of an existing eligibility claim
        :param personal_details: id of an existing
        personal details object
        :return: the created claim including the
        reference to give to the end user
        """
        data = {}
        data['eligibility_check'] = eligibility_check
        data['personal_details'] = personal_details
        return super(Case, self).create(data)
