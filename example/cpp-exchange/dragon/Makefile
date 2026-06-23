CXX := g++
CPP_ARGS := -I../../../include -I${DRAGON_INCLUDE_DIR} -std=c++20 -ldragon -L${DRAGON_LIB_DIR}

CLIENT_CPP = ../../../src/cpp/dragon.cpp

.PHONY: all
all: producer consumer

producer: producer.cpp
	${CXX} ${CPP_ARGS} -o producer ${CLIENT_CPP} ./producer.cpp

consumer: consumer.cpp
	${CXX} ${CPP_ARGS} -o consumer ${CLIENT_CPP} ./consumer.cpp


.PHONY: clean
clean:
	rm -f producer consumer ddict_orc_*
