/// <reference types="cypress" />
/// <reference types="cypress-downloadfile"/>

/**
 * @type {Cypress.PluginConfig}
 */


const {downloadFile} = require('cypress-downloadfile/lib/addPlugin')
module.exports = (on, config) => {
  on('task', {downloadFile})
}