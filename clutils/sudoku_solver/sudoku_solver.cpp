// Copyright (c) 2016 -2018 Matus Chochlik
//
#include <fstream>
#include "sudoku_solver.hpp"

int main(void) {

	sudoku_solver<4> s;

	s.read(std::cin);

	if(s.solve()) {
		s.print(std::cout) << std::endl;
	} else {
		std::cout << "cannot solve this board!" << std::endl;
	}

	return 0;
}

