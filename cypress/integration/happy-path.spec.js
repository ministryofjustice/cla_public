describe('Happy path testing', function() {
  it('Should complete happy path successfully from scope diagnosis to confirmation page', function () {

    cy.visit(Cypress.env('UAT_URL'))
    
    cy.contains('Choose the area you most need help with')
    cy.savePage('homepage')
    cy.contains('Debt').click()

    cy.contains('Choose the option that best describes your debt problem')
    cy.savePage('debt-options')
    cy.get(':nth-child(1) > .cla-scope-options-list-item-link').click()

    cy.contains('Legal aid is available for this type of problem')
    cy.savePage('scope-outcome')
    cy.contains('Check if you qualify financially').click()

    const generalMonetaryValue = 3245;

    // About you form
    cy.contains('.govuk-heading-xl', 'About you')
    cy.setYesNoRadioInput('have_partner', 'No')
    cy.setYesNoRadioInput('on_benefits', 'Yes')
    cy.setYesNoRadioInput('have_children', 'Yes')
    cy.setTextInput('num_children', '4')
    cy.setYesNoRadioInput('have_dependants', 'No')
    cy.setYesNoRadioInput('own_property', 'Yes')
    cy.setYesNoRadioInput('is_employed', 'No')
    cy.setYesNoRadioInput('is_self_employed', 'No')
    cy.setYesNoRadioInput('aged_60_or_over', 'No')
    cy.setYesNoRadioInput('have_savings', 'Yes')
    cy.setYesNoRadioInput('have_valuables', 'No')
    cy.savePage('about-you-form')
    cy.get("#submit-button").click();

    // Which benefits do you receive form
    cy.contains('.govuk-fieldset__heading', 'Which benefits do you receive?')
    cy.setCheckboxInput('benefits-5')
    cy.setCheckboxInput('benefits-6')
    cy.savePage('which-benefits-do-you-receive-form')
    cy.get("#submit-button").click();

    // Your additional benefits form
    cy.contains('.govuk-heading-xl', 'Your additional benefits')
    cy.setCheckboxInput('benefits-6')
    cy.setCheckboxInput('benefits-10')
    cy.setYesNoRadioInput('other_benefits', 'No')
    cy.savePage('additional-benefits-form')
    cy.get("#submit-button").click();

    // Your property form
    cy.contains('.govuk-heading-xl', 'Your property')
    cy.setYesNoRadioInput('properties-0-is_main_home', 'Yes')
    cy.setYesNoRadioInput('properties-0-other_shareholders', 'Yes')
    cy.setTextInput('properties-0-property_value', generalMonetaryValue)
    cy.setTextInput('properties-0-mortgage_remaining', generalMonetaryValue)
    cy.setTextInput('properties-0-mortgage_payments', generalMonetaryValue)
    cy.setYesNoRadioInput('properties-0-is_rented', 'Yes')
    cy.setTextInput('properties-0-rent_amount-per_interval_value', generalMonetaryValue)
    cy.setSelectInput('properties-0-rent_amount-interval_period', 'per_week')
    cy.setYesNoRadioInput('properties-0-in_dispute', 'Yes')
    cy.savePage('property-form')
    cy.get("#submit-button").click();

    // Your savings form
    cy.contains('.govuk-heading-xl', 'Your savings')
    cy.setTextInput('savings', generalMonetaryValue)
    cy.setTextInput('investments', generalMonetaryValue)
    cy.savePage('savings-form')
    cy.get("#submit-button").click();

    // Review your answers page
    cy.contains('.govuk-heading-xl', 'Review your answers')
    cy.savePage('review-page')
    cy.get("#submit-button").click();

    // Contact Civil Legal Advice page
    cy.contains('.govuk-heading-xl', 'Contact Civil Legal Advice')
    cy.setTextInput('full_name', 'Michael')
    cy.setRadioInput('contact_type-1')
    cy.setTextInput('callback-contact_number', '11111111111')
    cy.setRadioInput('callback-time-specific_day-1')
    cy.savePage('contact-CLA')
    cy.get("#submit-button").click();

    // Result confirmation page
    cy.contains('We will call you back')
    cy.contains('Receive this confirmation by email')
    cy.savePage('confirmation-page')
  });
})
