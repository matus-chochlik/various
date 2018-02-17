CXX ?= c++

# VARIANT_FLAGS = -g3
VARIANT_FLAGS = -O3 -DNDEBUG

CXXFLAGS = -std=c++14 -pedantic -Werror -Wall $(VARIANT_FLAGS)

all: $(foreach i, 2 3 4 5, sudoku_solver_$(i))

sudoku_solver_%: sudoku_solver.cpp $(wildcard *.hpp) Makefile
	$(CXX) $(CXXFLAGS) -DSUDOKU_SOLVER_RANK=$* -o $@ $<
