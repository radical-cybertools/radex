CXX := g++
CPP_ARGS := -I../../../include -std=c++20

SR_INCLUDE_DIR := /lus/scratch/drozt/repos/ssimdev/sr/install/include
SR_LIB_DIR := /lus/scratch/drozt/repos/ssimdev/sr/install/lib64

CPP_ARGS += -I${SR_INCLUDE_DIR} -L${SR_LIB_DIR} -lsmartredis


CLIENT_CPP = ../../../src/cpp/smartredis.cpp

.PHONY: all
all: producer consumer

producer: producer.cpp
	${CXX} ${CPP_ARGS} -o producer ${CLIENT_CPP} ./producer.cpp

consumer: consumer.cpp
	${CXX} ${CPP_ARGS} -o consumer ${CLIENT_CPP} ./consumer.cpp

.PHONY: clean
clean:
	rm -rf producer consumer cpp-sr-client-exchange
