function reasonsForContactingForm(client) {
  client
    .startService()
    .click('#callback-link', function() {
      console.log('     • "Get in touch" link clicked');
    })
    .waitForElementVisible('.reasons-for-contacting-form', 3000,
      '  - "Reasons for contacting" form exists');
  return client;
}

module.exports = {
  'Reasons for contacting do not need to be filled in': function(client) {
    reasonsForContactingForm(client);
    client
      .conditionalFormSubmit(true)
      .end()
    ;
  },

  'Reasons for contacting with one reason': function(client) {
    reasonsForContactingForm(client);
    client
      .click('input[value="PREFER_SPEAKING"]', function() {
        console.log('     • "I’d prefer to speak to someone" clicked');
      })
      .conditionalFormSubmit(true)
      .end()
    ;
  },

  'Reasons for contacting with more details': function(client) {
    reasonsForContactingForm(client);
    client
      .click('input[value="OTHER"]', function() {
        console.log('     • "Another reason" clicked');
      })
      .click('input[value="PREFER_SPEAKING"]', function() {
        console.log('     • "I’d prefer to speak to someone" clicked');
      })
      .conditionalFormSubmit(true)
      .end()
    ;
  }
};
