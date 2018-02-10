CXX ?= c++

CXXFLAGS = -std=c++14 -pedantic -Werror -Wall -O3

all: sudoku_solver_3 sudoku_solver_4

sudoku_solver_%: sudoku_solver.cpp $(wildcard *.hpp) Makefile
	$(CXX) $(CXXFLAGS) -DSUDOKU_SOLVER_RANK=$* -o $@ $<
