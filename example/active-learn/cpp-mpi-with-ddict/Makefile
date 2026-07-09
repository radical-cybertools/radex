CC ?= gcc
CXX ?= g++

CLIENT_INC = ../../../include
CLIENT_CPP = ../../../src/cpp/dragon.cpp

CFLAGS ?= -fPIC -Wall -O0 -g -fomit-frame-pointer -I$(CLIENT_INC)
# -D_GLIBCXX_USE_CXX11_ABI=0
#CFLAGS ?= -g -O0 -DDRAGON_DEBUG -Wall

ifeq ($(VIRTUAL_ENV),)
	VIRTUAL_ENV = $(CONDA_PREFIX)
endif

ifeq ($(DRAGON_INCLUDE_DIR),)
    DRAGON_INCLUDE = $(shell dragon-config -o)
else
    DRAGON_INCLUDE = -I$(DRAGON_INCLUDE_DIR)
endif

ifeq ($(DRAGON_LIB_DIR),)
    DRAGON_LINK = $(shell  dragon-config -l)
else
    DRAGON_LINK = -L$(shell echo ${DRAGON_LIB_DIR}) -ldragon
endif

CFLAGS += $(DRAGON_INCLUDE) --std=c++20
LDFLAGS += $(DRAGON_LINK)

.PHONY: all
all: simulation

.PHONY: clean
clean:
	rm -rf simulation ddict_orc_* asyncflow.session.*

simulation: simulation.cpp
	$(CXX) $(CFLAGS) -o $@ $^ $(CLIENT_CPP) $(LDFLAGS)
