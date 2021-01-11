describe('Mini test', function() {
  it('should work', function () {
    cy.visit("https://lga-1543-install-and-integra.staging.checklegalaid.service.gov.uk/start")

    cy.contains('Choose the area you most need help with')
    cy.contains('Debt').click()

    cy.contains('Choose the option that best describes your debt problem')
    cy.get(':nth-child(1) > .cla-scope-options-list-item-link').click()

    cy.contains('Legal aid is available for this type of problem')
    cy.contains('Check if you qualify financially').click()

    const randomValue = 3245;

    // About you form
    cy.contains('About you')
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
    cy.get("#submit-button").click();

    // Which benefits do you receive form
    cy.contains('Which benefits do you receive')
    cy.setCheckboxInput('benefits-5')
    cy.setCheckboxInput('benefits-6')
    cy.get("#submit-button").click();

    // Your additional benefits form
    cy.contains('Your additional benefits')
    cy.setCheckboxInput('benefits-6')
    cy.setCheckboxInput('benefits-10')
    cy.setYesNoRadioInput('other_benefits', 'No')
    cy.get("#submit-button").click();

    // Your property form
    cy.contains('Your property')
    cy.setYesNoRadioInput('properties-0-is_main_home', 'Yes')
    cy.setYesNoRadioInput('properties-0-other_shareholders', 'Yes')
    cy.setTextInput('properties-0-property_value', randomValue)
    cy.setTextInput('properties-0-mortgage_remaining', randomValue)
    cy.setTextInput('properties-0-mortgage_payments', randomValue)
    cy.setYesNoRadioInput('properties-0-is_rented', 'Yes')
    cy.setTextInput('properties-0-rent_amount-per_interval_value', randomValue)
    cy.setSelectInput('properties-0-rent_amount-interval_period', 'per_week')
    cy.setYesNoRadioInput('properties-0-in_dispute', 'Yes')
    cy.get("#submit-button").click();

    // Your savings form
    cy.contains('Your savings')
    cy.setTextInput('savings', randomValue)
    cy.setTextInput('investments', randomValue)
    cy.get("#submit-button").click();

    // Review your answers page
    cy.contains('Review your answers')
    cy.contains('Your problem area')
    cy.get("#submit-button").click();


    // Contact Civil Legal Advice page
    cy.contains('Contact Civil Legal Advice')
    cy.setTextInput('full_name', 'Michael')
    cy.setRadioInput('contact_type-1')
    cy.setTextInput('callback-contact_number', '11111111111')
    cy.setRadioInput('callback-time-specific_day-1')
    cy.setSelectInput('callback-time-day', 'Tuesday 12th')
    cy.setSelectInput('callback-time-time_in_day', '2:00 PM - 2:30 PM')
    cy.get("#submit-button").click();

    // Result confirmation page
    cy.contains('We will call you back')

  });
})
