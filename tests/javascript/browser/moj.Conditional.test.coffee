field_name = "your_problem-category"

casper.test.begin "Conditional content", (test) ->

  casper.start casper.base_url + "your_problem/", ->
    test.assertSelectorHasText "h1", "Your problem", "page has correct title"

  casper.then ->
    test.assertNotVisible ".Conditional", "conditional content not visible on load"
    test.assertExists "input[name=#{field_name}]", "option field exists"

  casper.thenEvaluate ((field) ->
    $("input[name=#{field}][data-conditional-el]").attr("checked", true).trigger "change"
  ), field_name

  casper.then ->
    test.assertVisible ".Conditional", "conditional content is visible"

  casper.thenEvaluate ((field) ->
    $("input[name=#{field}]:not([data-conditional-el])").attr("checked", true).trigger "change"
  ), field_name

  casper.then ->
    test.assertNotVisible ".Conditional", "conditional content is visible"

  casper.run ->
    test.done()