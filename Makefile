all: install run

debug: install_no_user run

run:
	./sfp_eval/bin/announcement_sim_ng.py ./data/coreemu/LHCOne-final.yaml ./data/cms-trace/ip-flows.json algorithm_types=123

install:
	./setup.py install --user

install_no_user:
	./setup.py install
