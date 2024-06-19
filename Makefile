install-git-hooks:
	cp .github/hooks/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

.PHONY: install-git-hooks

all: install-git-hooks run

openapi-gen:
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli generate \
    -i /local/openapis/naas-openapi.json \
    -g python \
	-c /local/openapis/naas-openapi.config.yaml \
    -o /local/openapis/clients/python/

openapi-gen-help:
	docker run --rm -v "${PWD}:/local" openapitools/openapi-generator-cli help generate

test_extra=-s
test:
	poetry run python -m pytest tests/ $(test_extra)

run:
	@echo "You should execute:\n\tpoetry run naas-python"