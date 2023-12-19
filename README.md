# Async-Requester

This is a wrapper around httpx and trio for making python requests easier and default to async.

The returned objects are httpx responses.

## Quickstart

Install [poetry](https://python-poetry.org/) then run:

```bash
poetry install
poetry run python -m src.main
```

## More

TODO: finish this readme explaining stuff

## Nice to have

* Backward compatible for pip (using `requirements.txt`) but uses Poetry package management
* Optional to send one request i.e. you don't need to provide multiple `RequestInfo` objects
* [Black](https://black.readthedocs.io/en/stable/index.html) formatted
* mypy compliant
* Modern http and async libraries ([httpx](https://www.python-httpx.org/) and [trio](https://trio.readthedocs.io/en/stable/) respectively)
