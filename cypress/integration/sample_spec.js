describe('Mini test', function() {
  it('should work', function () {
    cy.visit("https://lga-1543-install-and-integra.staging.checklegalaid.service.gov.uk/start")

    cy.contains('Choose the area you most need help with')
    cy.contains('Debt').click()

    cy.contains('Choose the option that best describes your debt problem')
    cy.get(':nth-child(1) > .cla-scope-options-list-item-link').click()

    cy.contains('Legal aid is available for this type of problem')
    cy.contains('Check if you qualify financially').click()

    // About you form
    cy.setRadioInput('have_partner', 'No')
    cy.setRadioInput('on_benefits', 'Yes')
    cy.setRadioInput('have_children', 'Yes')
    cy.setTextInput('num_children', '4')
    cy.setRadioInput('have_dependants', 'No')
    cy.setRadioInput('own_property', 'Yes')
    cy.setRadioInput('is_employed', 'No')
    cy.setRadioInput('is_self_employed', 'No')
    cy.setRadioInput('aged_60_or_over', 'No')
    cy.setRadioInput('have_savings', 'Yes')
    cy.setRadioInput('have_valuables', 'No')
    cy.get("#submit-button").click();

    // Which benefits do you receive form
    cy.setCheckboxInput('benefits-5')
    cy.setCheckboxInput('benefits-6')
    cy.get("#submit-button").click();



  });
})
