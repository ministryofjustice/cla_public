# Casper.js Integration Test Helpers

# Base URL
casper.base_url = casper.cli.get("url") || "http://0.0.0.0:8002/"

casper.startChecker = ->
  @start casper.base_url, ->

  @then ->
    @click "a[role=button]"

  @then ->
    @click "a[role=button]"


#
# ###### Clear cookies before the test run starts to avoid pollution.
#
casper.on 'run.start', ->
  @page.clearCookies()

#
# ###### Reset the URL hash after each test run completes to avoid pollution.
#
casper.on 'run.complete', ->
  @evaluate ->
    window.location.hash = ''