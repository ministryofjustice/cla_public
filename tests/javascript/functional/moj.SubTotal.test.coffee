field_name = "your_problem-category"

casper.test.begin "Subtotal Calculator", (test) ->

  # helpers method
  casper.startChecker()

  # Navigate to the page needed for tests
  casper.thenEvaluate ->
    $("input[name=your_problem-category]:first").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/
  casper.thenEvaluate ->
    $("input[value=1][type=radio]").click()
    $("input[value=0][name=your_details-has_benefits]").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_capital/
  casper.thenEvaluate ->
    $("input[type=number]").val(0)
    $("input[value=0][type=radio]").click()
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_income/
  casper.thenEvaluate ->
    $("input[type=number]").val(0)
  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_allowances/

  # check first section is calculated correctly
  casper.thenEvaluate ->
    $("#id_your_allowances-mortgage").val(50).keyup()
  casper.then ->
    @test.assertSelectorHasText {type: 'xpath', path: '//*[@id="content"]/div/form/section[1]/div/p/span'}, "£ 50.00", "first total calculated the correct value"
    @test.assertSelectorHasText {type: 'xpath', path: '//*[@id="content"]/div/form/section[2]/div/p/span'}, "£ 0.00", "second total remained at 0"

  # check second section is calculated correctly
  casper.thenEvaluate ->
    $("#id_partners_allowances-mortgage").val(75).keyup()
    $("#id_partners_allowances-rent").val(150).keyup()
  casper.then ->
    @test.assertSelectorHasText {type: 'xpath', path: '//*[@id="content"]/div/form/section[1]/div/p/span'}, "£ 50.00", "first total remained the same value"
    @test.assertSelectorHasText {type: 'xpath', path: '//*[@id="content"]/div/form/section[2]/div/p/span'}, "£ 225.00", "second total calculated the correct value"

  casper.run ->
    @test.done()

