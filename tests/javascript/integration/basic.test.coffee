casper.test.begin 'Site basics', suite = (test) ->

  casper.start casper.base_url, ->
    test.assertHttpStatus 200, 'site is up'

  casper.then ->
    test.assertSelectorHasText 'title', 'Civil Legal Advice', 'site contains the correct title'

  casper.run ->
    test.done()
