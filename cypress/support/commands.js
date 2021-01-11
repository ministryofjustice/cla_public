// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add("login", (email, password) => { ... })
//
//mm
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })

Cypress.Commands.add('setYesNoRadioInput', (selector, value) => {
  const selectorValue = value === 'Yes' ? '0' : '1'
  cy.get(`#${selector}-${selectorValue}`).check();
})

Cypress.Commands.add('setTextInput', (selector, value) => {
  cy.get(`#${selector}`).type(value);
})

Cypress.Commands.add('setCheckboxInput', selector => {
  cy.get(`#${selector}`).check();
})
Cypress.Commands.add('setSelectInput', (selector, value) => {
  cy.get(`#${selector}`).select(value);
})

Cypress.Commands.add('setRadioInput', selector => {
  cy.get(`#${selector}`).check();
})