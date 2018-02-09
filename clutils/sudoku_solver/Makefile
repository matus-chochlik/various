CXX ?= c++

all: sudoku_solver

sudoku_solver: sudoku_solver.cpp $(wildcard *.hpp) Makefile
	$(CXX) -std=c++14 -pedantic -Werror -Wall -O3 -o $@ $<
