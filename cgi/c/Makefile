CC = g++
CFLAGS = -Wall -O2 -std=c++11
SRC_DIR = src
BIN_DIR = bin
CGI_DIR = /var/www/cgi-bin

# Create bin directory if it doesn't exist
$(shell mkdir -p $(BIN_DIR))

all: $(BIN_DIR)/hello $(BIN_DIR)/form_handler

$(BIN_DIR)/hello: $(SRC_DIR)/hello.cpp
	$(CC) $(CFLAGS) -o $@ $<

$(BIN_DIR)/form_handler: $(SRC_DIR)/form_handler.cpp
	$(CC) $(CFLAGS) -o $@ $<

install: all
	sudo cp $(BIN_DIR)/hello $(CGI_DIR)/
	sudo cp $(BIN_DIR)/form_handler $(CGI_DIR)/
	sudo chmod +x $(CGI_DIR)/hello
	sudo chmod +x $(CGI_DIR)/form_handler
	sudo chown www-data:www-data $(CGI_DIR)/hello $(CGI_DIR)/form_handler

clean:
	rm -f $(BIN_DIR)/*

distclean: clean
	rmdir $(BIN_DIR) 2>/dev/null || true

test: all
	@echo "Testing hello program..."
	@QUERY_STRING="name=John&age=25" REQUEST_METHOD="GET" $(BIN_DIR)/hello > /tmp/hello_test.html
	@echo "Output saved to /tmp/hello_test.html"
	
	@echo "Testing form_handler program..."
	@QUERY_STRING="name=Jane&email=jane@example.com&message=Hello" REQUEST_METHOD="GET" $(BIN_DIR)/form_handler > /tmp/form_test.html
	@echo "Output saved to /tmp/form_test.html"

.PHONY: all install clean distclean test
