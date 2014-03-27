casper.test.begin "Start page", (test) ->
  casper.start "http://0.0.0.0:8001/", ->
    @test.assertSelectorHasText "h1", "Do you qualify for legal aid", "Start page has correct title"

  casper.then ->
    @test.assertExists "a[role=button]", "Start button exists"
    @test.assertSelectorHasText "a[role=button]", "Start", "Button has correct text"

  casper.run ->
    @test.done()