all: install run

debug: install_no_user run

run:
	./sfp_eval/bin/announcement_sim_ng.py ./data/coreemu/LHCOne-final.yaml ./data/cms-trace/ip-flows.json triangle=./data/coreemu/triangles.json algorithm_type=1234 network_ratio=0.3 prefix_ratio=0.3

install:
	./setup.py install --user

install_no_user:
	./setup.py install
