LIBIMPULSE=-limpulse -Wl,-rpath,.
MACHINE=`uname -m`
MAIN_BUILD_DIR=build
BUILD_DIR=$(MAIN_BUILD_DIR)/$(MACHINE)
COPY_DEFAULTS=COPYING README.md

all: impulse test

impulse: 
	mkdir -p $(BUILD_DIR)/impulse
	cp $(COPY_DEFAULTS) $(BUILD_DIR)/impulse
	cp impulse.py $(BUILD_DIR)/impulse
	gcc -pthread -Wall -fPIC -c\
		src/impulse.c -o $(BUILD_DIR)/impulse/impulse.o
	gcc -pthread -lpulse -lfftw3 -shared -Wl,-soname,libimpulse.so -fPIC\
		$(BUILD_DIR)/impulse/impulse.o -o $(BUILD_DIR)/impulse/libimpulse.so
	gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fPIC\
		-I/usr/include/python2.7 -c src/module.c -o $(BUILD_DIR)/impulse/module.o
	gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -L$(BUILD_DIR)/impulse/ $(LIBIMPULSE)\
		$(BUILD_DIR)/impulse/module.o -o $(BUILD_DIR)/impulse/impulse.so
	rm $(BUILD_DIR)/impulse/*.o

test: impulse
	mkdir -p $(BUILD_DIR)/test
	cp $(BUILD_DIR)/impulse/libimpulse.so $(BUILD_DIR)/test/
	gcc -c src/test-libimpulse.c -o $(BUILD_DIR)/test/test-libimpulse.o
	gcc -L$(BUILD_DIR)/test/ $(LIBIMPULSE)\
		$(BUILD_DIR)/test/test-libimpulse.o -o $(BUILD_DIR)/test/test-libimpulse
	rm $(BUILD_DIR)/test/test-libimpulse.o

clean:
	rm -rf $(MAIN_BUILD_DIR)
