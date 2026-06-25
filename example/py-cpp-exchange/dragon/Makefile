CXX := g++
CPP_ARGS := -I../../../include -I${DRAGON_INCLUDE_DIR} -std=c++20 -ldragon -L${DRAGON_LIB_DIR}

CLIENT_CPP = ../../../src/cpp/dragon.cpp

.PHONY: all
all: app

app: app.cpp
	${CXX} ${CPP_ARGS} -o app ${CLIENT_CPP} ./app.cpp

.PHONY: clean
clean:
	rm -f app ddict_orc_*
