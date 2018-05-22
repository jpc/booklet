INPUT_NAME=$(notdir $(INPUT_PDF))

browser: pages.json
	http-server -p 8100 -c-1

pages.json: pages/.pages_$(INPUT_NAME)
	find pages/ -name 'page-*.png' \
		| sort \
		| jq -R '{url: ., i: input_line_number, even: (input_line_number % 2 == 0)}' \
		| jq -rs '"window.all_pages = \(.);"' \
		> $@

pages/.pages_$(INPUT_NAME): $(INPUT_PDF)
	rm -rf pages && mkdir -p pages && gs -sDEVICE=pngalpha -o pages/page-%03d.png -r50 "$^"
	touch "$@"
