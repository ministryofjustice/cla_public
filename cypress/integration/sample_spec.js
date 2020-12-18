describe('Mini test', function() {
  it('should work', function () {
    cy.visit("https://lga-1543-install-and-integra.staging.checklegalaid.service.gov.uk/start")

    cy.contains('Choose the area you most need help with')
    cy.contains('Debt').click()

    cy.contains('Choose the option that best describes your debt problem')
    cy.get(':nth-child(1) > .cla-scope-options-list-item-link').click()

    cy.contains('Legal aid is available for this type of problem')
    cy.contains('Check if you qualify financially').click()

    cy.setRadioInput('have_partner')
    cy.setRadioInput('on_benefits', 'No')

    // cy.get("#submit-button").click();

  });
})
