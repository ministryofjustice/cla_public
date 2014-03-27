casper.test.begin "Start page", (test) ->
  casper.start "http://0.0.0.0:8001/", ->
    @test.assertSelectorHasText "h1", "Check if you can get legal aid", "Start page has correct title"

  casper.then ->
    @test.assertExists "a[role=button]", "Start button exists"

  casper.run ->
    @test.done()