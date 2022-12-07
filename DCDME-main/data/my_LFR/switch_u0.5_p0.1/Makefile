CC=g++
OPTS=-O3
PREFIX=~/bin

SOURCES=src/generator_base.cpp src/generator_switch.cpp src/history.cpp

all: switch hide expand birthdeath mergesplit

switch: ${SOURCES} src/*switch*.cpp
	$(CC) $(OPTS) -o bench_switch src/bench_switch.cpp

hide: ${SOURCES} src/*hide*.cpp 
	$(CC) $(OPTS) -o bench_hide src/bench_hide.cpp

expand: ${SOURCES} src/*expand*.cpp 
	$(CC) $(OPTS) -o bench_expand src/bench_expand.cpp
		
birthdeath: ${SOURCES} src/*birth*.cpp
	$(CC) $(OPTS) -o bench_birthdeath src/bench_birthdeath.cpp

mergesplit: ${SOURCES} src/*mergesplit*.cpp 
	$(CC) $(OPTS) -o bench_mergesplit src/bench_mergesplit.cpp

install:
	cp bench_* $(PREFIX)
	
clean:
	rm -f bench_switch bench_hide bench_expand bench_birthdeath bench_mergesplit

cleandata:
	rm -f *.dat *.comm *.edges
