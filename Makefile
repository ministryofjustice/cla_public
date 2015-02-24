test:
	./nightwatch -c tests/nightwatch/local.json -s legacy -t tests/nightwatch/specs/current/${spec}.js
test-chrome:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env chrome -t tests/nightwatch/specs/current/${spec}.js
test-firefox:
	./nightwatch -c tests/nightwatch/local.json -s legacy --env firefox -t tests/nightwatch/specs/current/${spec}.js
test-legacy:
	./nightwatch -c tests/nightwatch/local.json -s current -t tests/nightwatch/specs/current/${spec}.js
test-all:
	./nightwatch -c tests/nightwatch/local.json
