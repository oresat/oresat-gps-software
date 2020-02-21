
IDIR=/home/ubuntu/ftdi/release
INCLUDES=-I$(IDIR)

CFLAGS=-g -Wall
LDFLAGS=-lftd2xx

Setup_2232H_Test: Setup_2232H_Test.cpp max2769.o max2769.h
	gcc -o Setup_2232H_Test Setup_2232H_Test.cpp max2769.o $(CFLAGS) $(INCLUDES) $(LDFLAGS)

max2769.o: max2769.cpp max2769.h
	gcc -c max2769.cpp $(CFLAGS) $(INCLUDES)
