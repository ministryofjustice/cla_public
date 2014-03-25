casper.test.begin "Disposable Income not eligible because too much income", (test) ->

  phantom.clearCookies()
  casper.start casper.base_url + "your_problem/", ->
    test.assertSelectorHasText "h1", "Your problem", "page has correct title"

  casper.thenEvaluate ->
      $("input[name=your_problem-category]:first").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/

  casper.thenEvaluate ->
    $("input[value=0][type=radio]").click()
    $("#id_your_details-has_partner_0").click()

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
    $("#id_your_income-earnings").val(910.51)
    $("input[value=1][type=radio]").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_allowances/

  casper.thenEvaluate ->
    $("input[type=number]").val(0)

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*result/

  casper.then ->
    test.assertSelectorHasText "form h2", "not", "test case is not eligible"

  casper.run ->
    test.done()



casper.test.begin "Disposable Income is eligible because not enough income", (test) ->
  phantom.clearCookies()
  casper.start casper.base_url + "your_problem/", ->
    test.assertSelectorHasText "h1", "Your problem", "page has correct title"


  casper.thenEvaluate ->
    $("input[name=your_problem-category]:first").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_details/

  casper.thenEvaluate ->
    $("input[value=0][type=radio]").click()
    $("#id_your_details-has_partner_0").click()

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
    $("#id_your_income-earnings").val(910.5)
    $("input[value=1][type=radio]").click()

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*your_allowances/

  casper.thenEvaluate ->
    $("input[type=number]").val(0)

  casper.then ->
    @fill 'form', {}, true
    @waitForUrl /.*result/

  casper.then ->
    test.assertSelectorHasText "form h2", "might be", "test case is not eligible"

  casper.run ->
    test.done()
