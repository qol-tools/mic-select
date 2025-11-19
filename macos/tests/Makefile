.PHONY: test clean

CC = gcc
CFLAGS = -framework CoreAudio -framework CoreFoundation -Wall
TEST_SRC = test_aggregate_mic.c
TEST_BIN = test_aggregate_mic

test: $(TEST_BIN)
	@echo "Running macOS aggregate mic tests..."
	@./$(TEST_BIN)
	@echo ""

$(TEST_BIN): $(TEST_SRC)
	$(CC) $(CFLAGS) -o $(TEST_BIN) $(TEST_SRC)

clean:
	rm -f $(TEST_BIN)
