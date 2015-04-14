'use strict';

var util = require('util');
var common = require('../../modules/common-functions.js');

function text(n) {
  return Array(n + 1).join('x');
}

function contactPage(client) {
  common.startPage(client);
  client
    .click('#callback-link');
}

function willCallWithNotes(client, notes_text) {
  var notes = 'textarea[name="extra_notes"]';
  var length = notes_text.length;
  client
    .setValue('input#full_name', 'John Smith')
    .click('input[name="callback_requested"][value="0"]')
    .setValue(notes, notes_text)
    .assert.value(notes, notes_text, 'Notes set to ' + length + ' chars')
    .submitForm('form');
}

function assertNotesError(client) {
  client
    .assert.containsText('#field-extra_notes .field-error', 'Your notes must be 4000 characters or less');
}

function assertConfirmation(client) {
  client
    .assert.containsText('h1', 'Your details have been submitted');
}

module.exports = {
  'Notes max length is 4000 chars': function (client) {
    contactPage(client);

    willCallWithNotes(client, text(4001));
    assertNotesError(client);

    client.clearValue('textarea[name="extra_notes"]');

    willCallWithNotes(client, text(4000));
    assertConfirmation(client);

    client.end();
  }
}

//function assertNotes(length, assertFn) {
  //module.exports['Notes length ' + length] = function (client) {
    //contactPage(client);
    //willCallWithNotes(client, text(length));
    //assertFn(client);
    //client.end();
  //};
//}

//function assertNotesPass(length) {
  //assertNotes(length, assertConfirmation);
//}

//function assertNotesFail(length) {
  //assertNotes(length, assertNotesError);
//}

//!function () {
  //[0, 1, 5, 100, 1000, 4000].forEach(assertNotesPass);
  //[4001, 5000, 10000].forEach(assertNotesFail);
//}();
