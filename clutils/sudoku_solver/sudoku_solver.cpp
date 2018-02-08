// Copyright (c) 2016 -2018 Matus Chochlik
//
#include "sudoku_solver.hpp"

int main(void) {
	sudoku_solver s(4);
	s.read(std::cin);

	if(s.solve()) s.print(std::cout);
	else std::cout << "cannot solve this board!" << std::endl;

	return 0;
}

