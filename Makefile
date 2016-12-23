BUILD_DIR=build

all: impulse
	cp $(BUILD_DIR)/impulse.so impulse.so
	rm -rf $(BUILD_DIR)

init:
	mkdir -p $(BUILD_DIR)

impulse: init module.o impulse.o
	cp spectrumyzer.py $(BUILD_DIR)
	gcc -pthread -shared -Wl,-O2 -Bsymbolic-functions\
		-L$(BUILD_DIR)/ $(BUILD_DIR)/module.o\
		$(BUILD_DIR)/impulse.o -o $(BUILD_DIR)/impulse.so\
		-lfftw3 -lpulse

impulse.o:
	gcc -pthread -Wall -fPIC -c src/impulse.c -o $(BUILD_DIR)/impulse.o

module.o:
	gcc -pthread -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall\
		-Wstrict-prototypes -fPIC -I/usr/include/python3.5m \
		-c src/module.c -o $(BUILD_DIR)/module.o
