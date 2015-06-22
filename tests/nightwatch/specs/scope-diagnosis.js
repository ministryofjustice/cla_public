'use strict';

var scenarioTypes = {
  ineligible: {
    label: 'Ineligible',
    destination: '/scope/refer',
    identifier: 'a[href="https://www.gov.uk/find-a-legal-adviser"]'
  },
  inscope: {
    label: 'In scope',
    destination: '/about',
    identifier: 'input[name="have_partner"]'
  },
  f2f: {
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

var categories = [
  {
    name: 'Clinical negligence',
    scenarios: [
      {
        type: 'f2f',
        paths: [
          []
        ]
      }
    ]
  },
  {
    name: 'Debt',
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['You own your own home', 'Yes']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['You own your own home', 'No']
        ]
      }
    ]
  },
  {
    name: 'Domestic violence',
    scenarios: [
      {
        type: 'contact',
        paths: [
          ['Domestic violence', 'Yes']
        ]
      }
    ]
  }
];

module.exports = {

  'Scope diagnosis scenarios': function(client) {

    categories.forEach(function(category) {
      category.scenarios.forEach(function(scenario) {
        scenario.paths.forEach(function(path) {
          client
            .startService()
            .scopeDiagnosis(scenarioTypes[scenario.type].label, [category.name].concat(path))
            .waitForElementVisible(scenarioTypes[scenario.type].identifier, 5000,
              '  - Element ' + scenarioTypes[scenario.type].identifier + ' is present')
            .assert.urlContains(scenarioTypes[scenario.type].destination,
              '  - Destination page URL contains ' + scenarioTypes[scenario.type].destination);
        });
      });
    });

    client.end();
  }

};
