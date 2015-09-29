function reasonsForContactingForm(client) {
  client
    .startService()
    .click('#callback-link', function() {
      console.log('     ⟡ "Get in touch" link clicked');
    })
    .waitForElementVisible('.reasons-for-contacting-form', 3000,
      '  - "Reasons for contacting" form exists');
  return client;
}

function submitReasonsForContacting(client) {
  client.submitForm('.reasons-for-contacting-form', function() {
    console.log('     ⟡ "Continue to contact CLA" button clicked');
  }).waitForElementVisible('.contact-form', 5000,
    '  - Contact form loaded'
  );
}

module.exports = {
  'Reasons for contacting do not need to be filled in': function(client) {
    reasonsForContactingForm(client);
    submitReasonsForContacting(client);
    client.end();
  },

  'Reasons for contacting with one reason': function(client) {
    reasonsForContactingForm(client);
    client
      .click('input[value="PREFER_SPEAKING"]', function() {
        console.log('     ⟡ "I’d prefer to speak to someone" clicked');
      });
    submitReasonsForContacting(client);
    client.end();
  },

  'Reasons for contacting with more details': function(client) {
    reasonsForContactingForm(client);
    client
      .click('input[value="OTHER"]', function() {
        console.log('     ⟡ "Another reason" clicked');
      })
      .click('input[value="PREFER_SPEAKING"]', function() {
        console.log('     ⟡ "I’d prefer to speak to someone" clicked');
      });
    // free text field is no longer visible
    submitReasonsForContacting(client);
    client.end();
  }
};
