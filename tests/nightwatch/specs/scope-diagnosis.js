'use strict';

var constants = require('../modules/constants');

var scenarioTypes = {
  outOfScope: {
    label: 'Out of scope',
    destination: '/scope/refer',
    identifier: 'a[href="http://find-legal-advice.justice.gov.uk/"]'
  },
  inScope: {
    label: 'In scope',
    destination: '/legal-aid-available',
    identifier: 'a.button-get-started'
  },
  faceToFace: {
    label: 'Face to Face',
    destination: '/scope/refer/legal-adviser',
    identifier: 'input[name="postcode"]'
  },
  contact: {
    label: 'Contact',
    destination: '/contact',
    identifier: 'input[name="contact_type"]'
  }
};
var scenarios = [
  constants.SCOPE_PATHS.clinnegFaceToFace,
  constants.SCOPE_PATHS.domesticAbuseContact,
  constants.SCOPE_PATHS.debtOutOfScope,
  constants.SCOPE_PATHS.debtInScope
];

module.exports = {

  'Scope diagnosis scenarios': function(client) {

    scenarios.forEach(function(scenario) {
      var scenarioType = scenarioTypes[scenario.type];

      client
        .startService()
        .scopeDiagnosis(scenario)
        .waitForElementVisible(scenarioType.identifier, 5000,
          '  - Element ' + scenarioType.identifier + ' is present')
        .assert.urlContains(scenarioType.destination,
          '  - Destination page URL contains ' + scenarioType.destination);
    });

    client.end();
  }

};
