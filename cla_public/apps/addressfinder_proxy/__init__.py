"AddressFinder proxy app"
from flask import Blueprint

from api import lookup, lookup_postcode


addressfinder = Blueprint('addressfinder', __name__)
