// Copyright (c) 2016 -2018 Matus Chochlik
//
#include <fstream>
#include "sudoku_solver.hpp"

#ifndef SUDOKU_SOLVER_RANK
#define SUDOKU_SOLVER_RANK 3
#endif

int main(void) {

	sudoku_solver<SUDOKU_SOLVER_RANK> s;

	s.read(std::cin);

	if(s.solve()) {
		s.print(std::cout) << std::endl;
	} else {
		std::cout << "cannot solve this board!" << std::endl;
	}

	return 0;
}

