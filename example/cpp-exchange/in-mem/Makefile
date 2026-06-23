CXX := g++
CPP_ARGS := -I../../../include -std=c++20

.PHONY: all
all: proof 

proof: proof_of_concept_iface.cpp
	${CXX} ${CPP_ARGS} -o proof ./proof_of_concept_iface.cpp

.PHONY: clean
clean:
	rm -f proof
