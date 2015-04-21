'use strict';

var common = require('../../modules/common-functions');

var scenarios = [
  {
    name: 'In scope',
    nodes: ['Debt', 'You own your own home', 'Yes'],
    destination: '/scope/in-scope',
    identifier: 'a.continue'
  },
  {
    name: 'Category out of scope',
    nodes: ['Clinical negligence'],
    destination: '/result/face-to-face',
    identifier: 'input[name="postcode"]'
  },
  {
    name: 'Problem detail out of scope',
    nodes: ['Education', 'Admissions', 'Admission to school in the normal admissions round'],
    destination: '/result/face-to-face',
    identifier: 'input[name="postcode"]'
  },
  {
    name: 'Contact',
    nodes: ['Family', 'A problem with your ex-partner', 'Disputes over children', 'Domestic abuse', 'Yes'],
    destination: '/contact',
    identifier: 'input[name="third_party_handled"]'
  }
];

module.exports = {

  'Scope diagnosis scenarios': function(client) {

    scenarios.forEach(function(scenario) {
      common.startPage(client);
      client
        .scopeDiagnosis(scenario.name, scenario.nodes)
        .waitForElementVisible(scenario.identifier, 5000)
        .assert.urlContains(scenario.destination,
          'Destination page URL contains ' + scenario.destination)
      ;
    });

    client.end();
  }

};
