'use strict';

var common = require('../../modules/common-functions');
var log = require('../../modules/log');

var scenario_types = {
  ineligible: {
    destination: '/scope/ineligible',
    identifier: 'a[href="https://www.gov.uk/find-a-legal-adviser"]'
  },
  inscope: {
    destination: '/scope/in-scope',
    identifier: 'a.continue'
  },
  f2f: {
    destination: '/result/face-to-face',
    identifier: 'input[name="postcode"]'
  },
  contact: {
    destination: '/contact',
    identifier: 'input[name="third_party_handled"]'
  }
};

var categories = [
  {
    name: "Clinical negligence",
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
    name: "Community care",
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
    name: "Debt",
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['You own your own home', 'Yes'],
          ['You\'re living in rented accomodation', 'Becoming homeless'],
          ['You\'re living in rented accomodation', 'Eviction', 'Unlawful eviction'],
          ['You\'re living in rented accomodation', 'Eviction', 'Eviction with notice'],
          ['You\'re living in rented accomodation', 'Housing disrepair'],
          ['You\'re living in rented accomodation', 'Harassment', 'A neighbour or your landlord'],
          ['You\'re living in rented accomodation', 'Harassment', 'A partner, ex-partner or family member', 'No'],
          ['You\'re living in rented accomodation', 'ASBO or ASBI', 'A social housing landlord']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['You\'re living in rented accomodation', 'Eviction', 'None of the above'],
          ['You\'re living in rented accomodation', 'Harassment', 'Someone else'],
          ['You\'re living in rented accomodation', 'ASBO or ASBI', 'A private landlord'],
          ['You\'re living in rented accomodation', 'None of the above']
        ]
      },
      {
        type: 'contact',
        paths: [
          ['You\'re living in rented accomodation', 'Harassment', 'A partner, ex-partner or family member', 'Yes']
        ]
      }
    ]
  },
  {
    name: 'Domestic violence',
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['Domestic violence', 'No'],
          ['Enforcing an injunction', 'No'],
          ['Harassment', 'No'],
          ['Contesting an injunction'],
          ['Forced marriage'],
          ['Child abduction']
        ]
      },
      {
        type: 'contact',
        paths: [
          ['Domestic violence', 'Yes'],
          ['Enforcing an injunction', 'Yes'],
          ['Harassment', 'Yes']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['Any other problem']
        ]
      }
    ]
  },
  {
    name: 'Discrimination',
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['Age', '18 or over', 'At work'],
          ['Age', '18 or over', 'While you were using a service'],
          ['Age', '18 or over', 'At a private club'],
          ['Age', '18 or over', 'When someone was carrying out a public function'],
          ['Age', '18 or over', 'At university'],
          ['Age', 'Under 18', 'At work'],
          ['Age', 'Under 18', 'At a private club'],
          ['Age', 'Under 18', 'At university'],
          ['Disability', 'At work'],
          ['Disability', 'While you were using a service'],
          ['Disability', 'At a private club'],
          ['Disability', 'When someone was carrying out a public function'],
          ['Disability', 'At school or college'],
          ['Disability', 'At university'],
          ['Gender, gender reassignment or sexual orientation', 'At work'],
          ['Gender, gender reassignment or sexual orientation', 'While you were using a service'],
          ['Gender, gender reassignment or sexual orientation', 'At a private club'],
          ['Gender, gender reassignment or sexual orientation', 'When someone was carrying out a public function'],
          ['Gender, gender reassignment or sexual orientation', 'At school or college'],
          ['Gender, gender reassignment or sexual orientation', 'At university'],
          ['Marriage or civil partnership', 'At work'],
          ['Pregnancy or maternity', 'At work'],
          ['Pregnancy or maternity', 'While you were using a service'],
          ['Pregnancy or maternity', 'At a private club'],
          ['Pregnancy or maternity', 'When someone was carrying out a public function'],
          ['Pregnancy or maternity', 'At school or college'],
          ['Pregnancy or maternity', 'At university'],
          ['Race', 'At work'],
          ['Race', 'While you were using a service'],
          ['Race', 'At a private club'],
          ['Race', 'When someone was carrying out a public function'],
          ['Race', 'At school or college'],
          ['Race', 'At university'],
          ['Religion, belief, or lack of religion or belief', 'At work'],
          ['Religion, belief, or lack of religion or belief', 'While you were using a service'],
          ['Religion, belief, or lack of religion or belief', 'At a private club'],
          ['Religion, belief, or lack of religion or belief', 'When someone was carrying out a public function'],
          ['Religion, belief, or lack of religion or belief', 'At school or college'],
          ['Religion, belief, or lack of religion or belief', 'At university']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['Age', '18 or over', 'Other'],
          ['Age', 'Under 18', 'Other'],
          ['Disability', 'Other'],
          ['Gender, gender reassignment or sexual orientation', 'Other'],
          ['Marriage or civil partnership', 'Other'],
          ['Pregnancy or maternity', 'Other'],
          ['Race', 'Other'],
          ['Religion, belief, or lack of religion or belief', 'Other'],
          ['None of the above']
        ]
      }
    ]
  },
  {
    name: 'Education',
    scenarios: [
      {
        type: 'contact',
        paths: [
          ['A child in care or a care leaver - or you are a foster carer']
        ]
      },
      {
        type: 'inscope',
        paths: [
          ['Special educational needs'],
          ['Admissions', 'Appeals'],
          ['Admissions', 'Waiting for an admissions decision'],
          ['Admissions', 'Further education admissions'],
          ['Admissions', 'Higher education admissions'],
          ['Exclusions or a child or young person being out of school', 'Child or young person out of school'],
          ['Exclusions or a child or young person being out of school', 'Exclusion from school', 'Suspension'],
          ['Exclusions or a child or young person being out of school', 'Exclusion from school', 'Permanent exclusion'],
          ['Exclusions or a child or young person being out of school', 'Exclusion from further education or higher education', 'No'],
          ['Transport to place of education'],
          ['Higher education fees and funding']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['Admissions', 'Admission to school in the normal admissions round'],
          ['Admissions', 'Any other admissions problem'],
          ['Exclusions or a child or young person being out of school', 'Exclusion from school', 'Any other exclusion problem'],
          ['Exclusions or a child or young person being out of school', 'Exclusion from further education or higher education', 'Yes'],
          ['None of the above']
        ]
      }
    ]
  },
  {
    name: 'Employment',
    scenarios: [
      {
        type: 'ineligible',
        paths: [
          ['Any other problem']
        ]
      }
    ]
  },
  {
    name: 'Family',
    scenarios: [
      {
        type: 'contact',
        paths: [
          ['Your local council is involved', 'Yes'],
          ['A problem with your ex-partner', 'Divorce or separation', 'Domestic abuse', 'Yes']
        ]
      },
      {
        type: 'inscope',
        paths: [
          ['Your local council is involved', 'No'],
          ['A problem with your ex-partner', 'Divorce or separation', 'You are under 18'],
          ['A problem with your ex-partner', 'Divorce or separation', 'Domestic abuse', 'No'],
          ['A problem with your ex-partner', 'Disputes over children', 'You are under 18'],
          ['A problem with your ex-partner', 'Disputes over children', 'Domestic abuse', 'No'],
          ['A problem with your ex-partner', 'Financial settlement', 'You are under 18'],
          ['A problem with your ex-partner', 'Financial settlement', 'Domestic abuse', 'No'],
          ['A problem with your ex-partner', 'Financial settlement', 'International Family Maintenance'],
          ['Child abduction']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['A problem with your ex-partner', 'Divorce or separation', 'Any other problem'],
          ['A problem with your ex-partner', 'Disputes over children', 'Any other problem'],
          ['A problem with your ex-partner', 'Financial settlement', 'Any other problem'],
          ['A problem with your ex-partner', 'Any other problem'],
          ['Any other problem']
        ]
      }
    ]
  },
  {
    name: "Housing",
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['You own your own home', 'Yes'],
          ['You\'re living in rented accomodation', 'Becoming homeless'],
          ['You\'re living in rented accomodation', 'Eviction', 'Unlawful eviction'],
          ['You\'re living in rented accomodation', 'Eviction', 'Eviction with notice'],
          ['You\'re living in rented accomodation', 'Housing disrepair'],
          ['You\'re living in rented accomodation', 'Harassment', 'A neighbour or your landlord'],
          ['You\'re living in rented accomodation', 'Harassment', 'A partner, ex-partner or family member', 'No'],
          ['You\'re living in rented accomodation', 'ASBO or ASBI', 'A social housing landlord']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['You\'re living in rented accomodation', 'Eviction', 'None of the above'],
          ['You\'re living in rented accomodation', 'Harassment', 'Someone else'],
          ['You\'re living in rented accomodation', 'ASBO or ASBI', 'A private landlord'],
          ['You\'re living in rented accomodation', 'None of the above']
        ]
      },
      {
        type: 'contact',
        paths: [
          ['You\'re living in rented accomodation', 'Harassment', 'A partner, ex-partner or family member', 'Yes']
        ]
      }
    ]
  },
  {
    name: 'Immigration and asylum',
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['Yes']
        ]
      },
      {
        type: 'f2f',
        paths: [
          ['No']
        ]
      }
    ]
  },
  {
    name: "Mental health",
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
    name: "Personal injury",
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
    name: "Public law",
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
    name: "Trouble with the police",
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
    name: "Welfare benefits",
    scenarios: [
      {
        type: 'inscope',
        paths: [
          ['Benefits appeal'],
          ['Permission to appeal refused']
        ]
      },
      {
        type: 'ineligible',
        paths: [
          ['None of the above']
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
          common.startPage(client);
          client
            .scopeDiagnosis([category.name].concat(path))
            .waitForElementVisible(scenario_types[scenario.type].identifier, 5000,
              '  - Element ' + scenario_types[scenario.type].identifier + ' is present')
            .assert.urlContains(scenario_types[scenario.type].destination,
              '  - Destination page URL contains ' + scenario_types[scenario.type].destination)
        });
      });
    });

    client.end();
  }

};
