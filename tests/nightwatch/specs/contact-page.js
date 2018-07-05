'use strict';

function text(n) {
  return new Array(n + 1).join('x');
}

function contactPage(client) {
  client
    .startService()
    .click('#callback-link', function() {
      console.log('     ⟡ "Get in touch" link clicked');
    })
    .waitForElementVisible('.reasons-for-contacting-form', 3000,
      '    - "Reasons for contacting" form exists')
    .conditionalFormSubmit(true)
  ;
}

function willCallWithNotes(client, notes_text) {
  var notes = 'textarea[name="extra_notes"]';
  var length = notes_text.length;
  client
    .setValue('input[name="full_name"]', 'John Smith')
    .click('input[name="contact_type"][value="call"]')
    .setValue(notes, notes_text)
    .assert.value(notes, notes_text,
      '    - Notes set to ' + length + ' chars')
    .conditionalFormSubmit(true)
  ;
}

module.exports = {
  '@disabled': true,
  'Notes max length is 4000 chars': function (client) {
    contactPage(client);
    willCallWithNotes(client, text(4000));
    client
      .waitForElementVisible('.confirmation', 3000,
        '    - Confirmation block exists')
      .assert.containsText('h1', 'Your details have been submitted',
        '    - Confirmation title exists'
      )
    ;
  },

  'Notes have counter': function(client) {
    contactPage(client);

    client
      .setValue('textarea[name="extra_notes"]', text(2000), function() {
        console.log('       • Adding 2000 characters in notes field');
      })
      .assert.containsText('.character-counter', 2000,
        '    - Checking that notes counter shows 2000 left')
      .setValue('textarea[name="extra_notes"]', text(1980), function() {
        console.log('       • Adding another 1980 characters');
      })
      .assert.containsText('.character-counter', 20,
        '    - Checking that notes counter shows 20 left')
      .assert.cssClassPresent('.character-counter', 'counter-low',
        '    - Counter class should change to ‘low character’ mode')
      .setValue('textarea[name="extra_notes"]', text(30), function() {
        console.log('       • Overflowing notes field with 10 characters over the limit');
      })
      .assert.containsText('.character-counter', 0,
        '    - Checking that notes counter shows 0')
      .getValue('textarea[name="extra_notes"]', function(response) {
        this.assert.ok(response.value.length === 4000,
          'Ensure that number of characters in notes field is still 4000');
      });

    client.end();
  }
};
