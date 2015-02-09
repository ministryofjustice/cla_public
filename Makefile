test:
	./nightwatch -c tests/nightwatch/local.json -s legacy -t ${test}
test-chrome:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env chrome -t ${test}
test-firefox:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env firefox -t ${test}
test-legacy:
	./nightwatch -c tests/nightwatch/local.json -s current -t ${test}
test-all:
	./nightwatch -c tests/nightwatch/local.json
