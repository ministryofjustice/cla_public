casper.test.begin "Validation test", (test) ->
  
  # helpers method
  casper.startChecker()

  casper.thenEvaluate ->
    $("input[name=your_problem-category]:first").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/

  # Fail Your Details validation
  casper.then ->
    @test.comment("Your Problem Validation");
    @fill 'form', {}, true
  casper.then ->
    @test.assertExists ".ErrorSummary", "your problem error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your problem error summary has correct title"
    @test.assertExists ".FormRow.Error", "your problem individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "required", "your problem individual error has correct text"

  # Pass Your Details page
  casper.thenEvaluate ->
    $("input[value=0][type=radio]").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_capital/
  casper.then ->
    @test.assertUrlMatch /.*your_capital/, "passed your details validation"

  # Fail Your Capital validation
  casper.then ->
    @test.comment("Your Capital Validation");
    @fill 'form', {}, true
  casper.then ->
    @test.assertExists ".ErrorSummary", "your capital error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your capital error summary has correct title"
    @test.assertExists ".FormRow.Error", "your capital individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "required", "your capital individual error has correct text"

  # Pass Your Capital page
  casper.thenEvaluate ->
    $("input[type=number]").val(0)
    $("input[value=1][type=radio]").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_income/
  casper.then ->
    @test.assertUrlMatch /.*your_income/, "passed your capital validation"

  # Fail Your Income validation
  casper.then ->
    @test.comment("Your Income Validation");
    @fill 'form', {}, true
  casper.then ->
    @test.assertExists ".ErrorSummary", "your income error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your income error summary has correct title"
    @test.assertExists ".FormRow.Error", "your income individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "required", "your income individual error has correct text"

  # Pass Your Capital page
  casper.thenEvaluate ->
    $("input[type=number]").val(0)
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_allowances/
  casper.then ->
    @test.assertUrlMatch /.*your_allowances/, "passed your income validation"

  # Fail Your Allowances validation
  casper.then ->
    @test.comment("Your Allowances Validation");
    @fill 'form', {}, true
  casper.then ->
    @test.assertExists ".ErrorSummary", "your allowances error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your allowances error summary has correct title"
    @test.assertExists ".FormRow.Error", "your allowances individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "required", "your allowances individual error has correct text"

  # Pass Your Capital page
  casper.thenEvaluate ->
    $("input[type=number]").val(0)
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*result/
  casper.then ->
    @test.assertUrlMatch /.*result/, "passed all validation"


  casper.run ->
    @test.done()