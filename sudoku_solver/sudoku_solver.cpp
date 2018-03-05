// Copyright (c) 2016 -2018 Matus Chochlik
//
#include <fstream>
#include <string>
#include "sudoku_solver.hpp"

#ifndef SUDOKU_SOLVER_RANK
#define SUDOKU_SOLVER_RANK 3
#endif

int main(int argc, const char** argv) {

	sudoku_options options;

	for(int a=1; a<argc; ++a) {
		const std::string arg(argv[a]);
		if(arg == "--variant") {
			++a;
			if(argv[a]) {
				options.variant = std::atoi(argv[a]);
			}
		} else if(arg == "--depth-first") {
			options.depth_first = true;
		} else if(arg == "--breadth-first") {
			options.depth_first = false;
		} else if(arg == "--sort") {
			options.sort_cells = true;
		} else if(arg == "--no-sort") {
			options.sort_cells = false;
		} else if(arg == "--random") {
			options.randomize_cells = true;
		} else if(arg == "--no-random") {
			options.randomize_cells = false;
		} else if(arg == "--fancy") {
			options.print_fancy = true;
		} else if(arg == "--plain") {
			options.print_fancy = false;
		} else if(arg == "--pango") {
			options.pango_markup = true;
		} else if(arg == "--no-pango") {
			options.pango_markup = false;
		} else if(arg == "--backtrace") {
			options.print_backtrace = true;
		} else if(arg == "--no-backtrace") {
			options.print_backtrace = false;
		} else {
			std::cerr << "error: unknown option `" << arg << "'" << std::endl;
			return 1;
		}
	}

	sudoku_solver<SUDOKU_SOLVER_RANK> solver;

	solver.read(std::cin);

	if(solver.solve(options)) {
		solver.print(std::cout, options) << std::endl;
	} else {
		std::cerr << "error: cannot solve this board!" << std::endl;
	}

	return 0;
}

