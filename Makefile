ARCH=`uname -m`
MAIN_BUILD_DIR=build
BUILD_DIR=$(MAIN_BUILD_DIR)/$(ARCH)
COPY_DEFAULTS=COPYING README.md

all: impulse test
	rm $(BUILD_DIR)/impulse/*.o
	rm $(BUILD_DIR)/test/*.o

init:
	mkdir -p $(BUILD_DIR)/impulse
	mkdir -p $(BUILD_DIR)/test
	cp $(COPY_DEFAULTS) $(BUILD_DIR)/impulse

impulse: init module.o impulse.o
	cp impulse.py $(BUILD_DIR)/impulse
	gcc -pthread -shared -Wl,-O2 -Bsymbolic-functions -lfftw3 -lpulse\
		-L$(BUILD_DIR)/impulse/ $(BUILD_DIR)/impulse/module.o\
		$(BUILD_DIR)/impulse/impulse.o -o $(BUILD_DIR)/impulse/impulse.so

test: impulse.o
	gcc -c src/test-impulse.c -o $(BUILD_DIR)/test/test-impulse.o
	gcc -L$(BUILD_DIR)/test/ -lfftw3 -lpulse\
		$(BUILD_DIR)/impulse/impulse.o $(BUILD_DIR)/test/test-impulse.o\
		-o $(BUILD_DIR)/test/test-impulse

impulse.o:
	gcc -pthread -Wall -fPIC -c src/impulse.c -o $(BUILD_DIR)/impulse/impulse.o

module.o:
	gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall\
		-Wstrict-prototypes -fPIC -I/usr/include/python2.7 \
		-c src/module.c -o $(BUILD_DIR)/impulse/module.o

clean:
	rm -rf $(MAIN_BUILD_DIR)
