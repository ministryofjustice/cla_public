field_name = "your_problem-category"

casper.test.begin "Conditional content", (test) ->

  casper.start casper.base_url + "your_problem/", ->
    test.assertSelectorHasText "h1", "Your problem", "page has correct title"

  casper.then ->
    test.assertNotVisible "#conditional-rHeXR", "conditional content not visible on load"
    test.assertExists "input[name=#{field_name}]", "option field exists"

  casper.thenEvaluate ((field) ->
    $("input[name=#{field}]:last").attr("checked", true).trigger "change"
  ), field_name

  casper.then ->
    test.assertVisible "#conditional-rHeXR", "conditional content is visible"

  casper.thenEvaluate ((field) ->
    $("input[name=#{field}]:first").attr("checked", true).trigger "change"
  ), field_name

  casper.then ->
    test.assertNotVisible "#conditional-rHeXR", "conditional content is visible"

  casper.run ->
    test.done()