casper.test.begin "Checker Validation tests", (test) ->
  
  # helpers method
  casper.startChecker()

  # Fail Your Problem validation
  casper.then ->
    @test.comment("Your Problem Validation");
    @fill 'form', {}, true
    @waitForUrl /.*your_problem/
  casper.then ->
    @test.assertUrlMatch /.*your_problem/, "correctly stayed on your problem page"
    @test.assertExists ".ErrorSummary", "your details error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your details error summary has correct title"
    @test.assertExists ".FormRow.Error", "your details individual error exists"

  # Pass Your Details page
  casper.thenEvaluate ->
    $("input[name=your_problem-category]:first").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/
  casper.then ->
    @test.assertUrlMatch /.*your_details/, "passed your problem validation"

  # Fail Your Details validation
  casper.then ->
    @test.comment("Your Details Validation");
    @fill 'form', {}, true
    @waitForUrl /.*your_details/
  casper.then ->
    @test.assertUrlMatch /.*your_details/, "correctly stayed on your details page"
    @test.assertExists ".ErrorSummary", "your details error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your details error summary has correct title"
    @test.assertExists ".FormRow.Error", "your details individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "cannot be blank", "your details individual error has correct text"

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
    @waitForUrl /.*your_capital/
  casper.then ->
    @test.assertUrlMatch /.*your_capital/, "correctly stayed on your capital page"
    @test.assertExists ".ErrorSummary", "your capital error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your capital error summary has correct title"
    @test.assertExists ".FormRow.Error", "your capital individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "cannot be blank", "your capital individual error has correct text"

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
    @waitForUrl /.*your_income/
  casper.then ->
    @test.assertUrlMatch /.*your_income/, "correctly stayed on your income page"
    @test.assertExists ".ErrorSummary", "your income error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your income error summary has correct title"
    @test.assertExists ".FormRow.Error", "your income individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "cannot be blank", "your income individual error has correct text"

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
    @waitForUrl /.*your_allowances/
  casper.then ->
    @test.assertUrlMatch /.*your_allowances/, "correctly stayed on your allowances page"
    @test.assertExists ".ErrorSummary", "your allowances error summary exists"
    @test.assertSelectorHasText ".ErrorSummary", "There was a problem submitting the form", "your allowances error summary has correct title"
    @test.assertExists ".FormRow.Error", "your allowances individual error exists"
    @test.assertSelectorHasText ".FormRow.Error", "cannot be blank", "your allowances individual error has correct text"

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