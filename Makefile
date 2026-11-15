PY ?= .venv/bin/python
TASK ?= ordinal-teens
POLICY ?= oracle
GRADER ?= v2
EPISODES ?= 1

.PHONY: setup tasks test run grade play study harbor

setup:
	python3 -m venv .venv
	$(PY) -m pip install -q pytest==8.3.3

tasks:
	$(PY) -B scripts/build_tasks.py

test:
	$(PY) -m pytest -q

run:
	$(PY) -m rlenv run --task $(TASK) --policy $(POLICY) --grader $(GRADER) --episodes $(EPISODES)

grade:
	$(PY) -m rlenv grade --task $(TASK) --file $(FILE)

play:
	$(PY) -m rlenv play --task $(TASK) --grader $(GRADER)

study:
	rm -f runs/study.jsonl
	$(PY) -m rlenv study --episodes $(EPISODES)
	$(PY) scripts/check_study.py runs/study.jsonl

harbor:
	scripts/harbor_check.sh
