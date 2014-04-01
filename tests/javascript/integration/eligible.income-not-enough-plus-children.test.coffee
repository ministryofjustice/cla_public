casper.test.begin "Disposable Income is eligible because not enough income and with children", (test) ->
  
  # helpers method
  casper.startChecker()

  casper.thenEvaluate ->
    $("input[name=your_problem-category]:first").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/

  casper.thenEvaluate ->
    $("input[value=0][type=radio]").click()
    $("#id_your_details-has_children_0").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_capital/

  casper.thenEvaluate ->
    $("input[type=number]").val(0)

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_income/

  casper.thenEvaluate ->
    $("input[type=number]").val(0)
    $("#id_your_income-earnings").val(732.99+(285.13*3))
    $("input[value=1][type=radio]").click()
    $("#id_dependants-dependants_old").val(2)
    $("#id_dependants-dependants_young").val(1)

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_allowances/

  casper.thenEvaluate ->
    $("input[type=number]").val(0)

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*result/

  casper.then ->
    @test.assertSelectorHasText "form h2", "might be", "test case might be eligible"

  casper.run ->
    @test.done()