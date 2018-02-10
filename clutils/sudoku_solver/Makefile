CXX ?= c++

CXXFLAGS = -std=c++14 -pedantic -Werror -Wall -g

all: $(foreach i, 2 3 4 5, sudoku_solver_$(i))

sudoku_solver_%: sudoku_solver.cpp $(wildcard *.hpp) Makefile
	$(CXX) $(CXXFLAGS) -DSUDOKU_SOLVER_RANK=$* -o $@ $<
