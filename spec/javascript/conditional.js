var url = casper.cli.get('url');

casper.start(url + '/your_problem', function() {

  casper.test.comment('Testing conditional content');

  casper.test.comment('hidden on load');
  this.test.assertNotVisible('#conditional-rHeXR');

  this.test.assertExists('input[name=your_problem-category][value=rHeXR]');

  this.evaluate(function(term) {
    document.querySelector('input[name=your_problem-category][value=rHeXR]').setAttribute('checked', true);
    $('input[name=your_problem-category]').trigger('change');
  });
  this.test.assertVisible('#conditional-rHeXR');

  this.evaluate(function(term) {
    document.querySelector('input[name=your_problem-category][value=WqIKJ]').setAttribute('checked', true);
    $('input[name=your_problem-category]').trigger('change');
  });
  this.test.assertNotVisible('#conditional-rHeXR');

});

casper.run(function() {
  this.test.done();
});