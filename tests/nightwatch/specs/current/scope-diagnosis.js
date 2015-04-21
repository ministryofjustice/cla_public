'use strict';

var common = require('../../modules/common-functions');

var scenarios = [
  {
    name: 'In scope',
    nodes: ['Debt', 'You own your own home', 'Yes'],
    destination: '/about',
    continue: true
  },
  {
    name: 'Category out of scope',
    nodes: ['Clinical negligence'],
    destination: '/result/face-to-face',
    continue: false
  },
  {
    name: 'Problem detail out of scope',
    nodes: ['Education', 'Admissions', 'Admission to school in the normal admissions round'],
    destination: '/result/face-to-face',
    continue: false
  },
  {
    name: 'Contact',
    nodes: ['Family', 'A problem with your ex-partner', 'Disputes over children', 'Domestic abuse', 'Yes'],
    destination: '/contact',
    continue: false
  }
];

module.exports = {

  'Scope diagnosis scenarios': function(client) {

    scenarios.forEach(function(scenario) {
      common.startPage(client);
      client
        .scopeDiagnosis(scenario.name, scenario.nodes, scenario.continue)
        .assert.urlContains(scenario.destination,
          'Destination page URL contains ' + scenario.destination)
      ;
    });

    client.end();
  }

};
