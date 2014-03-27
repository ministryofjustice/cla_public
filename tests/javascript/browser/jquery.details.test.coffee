field_name = "your_problem-category"

casper.test.begin "Details tag", (test) ->

  casper.start casper.base_url + "checker/your_problem/", ->
    test.assertSelectorHasText "h1", "Your problem", "page has correct title"

  casper.then ->
    test.assertExists "details", "has details tag"
    test.assertNotVisible "details > div", "details content is not visible"

  casper.thenEvaluate ((term) ->
    $("details:first").find('summary').click().trigger('click')
  ), ""

  casper.then ->
    test.assertVisible "details > *", "details content is visible"

  casper.run ->
    test.done()
