test:
	casperjs test ./tests/javascript/functional/ ./tests/javascript/integration/ --includes=./tests/javascript/casper-helpers.coffee --xunit=xunit.xml

test-nw:
	./nightwatch -c tests/javascript/nightwatch.json
test-jenkins:
	./nightwatch -c tests/javascript/nightwatch.json --env integration
