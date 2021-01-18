require('cypress-downloadfile/lib/downloadFileCommand')

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

Cypress.Commands.add('savePage', fileName => {
  cy.url().then(url => {
    cy.downloadFile(url, 'cypress/pages' , `${fileName}.html`)
  })
})