describe('Mini test', function() {
  it('should work', function () {
    cy.visit("https://lga-1543-install-and-integra.staging.checklegalaid.service.gov.uk/start")

    cy.contains('Choose the area you most need help with')
    cy.contains('Debt').click()

    cy.contains('Choose the option that best describes your debt problem')
    cy.get(':nth-child(1) > .cla-scope-options-list-item-link').click()

    cy.contains('Legal aid is available for this type of problem')
    cy.contains('Check if you qualify financially').click()

    // About you page form
    cy.setRadioInput('have_partner', 'Yes')
    cy.setRadioInput('in_dispute', 'No')  // Depends on have_partner being set to 'Yes'
    cy.setRadioInput('on_benefits', 'Yes')
    cy.setRadioInput('have_children')
    cy.setRadioInput('have_dependants')
    cy.setRadioInput('own_property')
    cy.setRadioInput('is_employed')
    cy.setRadioInput('is_self_employed')
    cy.setRadioInput('aged_60_or_over')
    cy.setRadioInput('have_savings')
    cy.setRadioInput('have_valuables')

    // cy.get("#submit-button").click();

  });
})
