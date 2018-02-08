CXX ?= c++

all: sudoku_solver

sudoku_solver: sudoku_solver.cpp $(wildcard *.hpp)
	$(CXX) -std=c++14 -pedantic -Wall -o $@ $<
