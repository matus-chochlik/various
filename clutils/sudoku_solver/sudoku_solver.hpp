// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_SOLVER_HPP
#define SUDOKU_SOLVER_HPP

#include "sudoku_board.hpp"
//------------------------------------------------------------------------------
template <int Rank>
class sudoku_solver {
private:
	sudoku_board<Rank> _board;
public:
	sudoku_solver(void) = default;

	void read(std::istream& input) {
		_board.read(input);
	}

	std::ostream& print(std::ostream& output) {
		return _board.print(output);
	}

	std::ostream& print_counts(std::ostream& output) {
		return _board.print_counts(output);
	}

	static bool solve_board(int r0, int c0, sudoku_board<Rank>& b, int depth);

	bool solve(void) {
		return solve_board(0, 0, _board, 0);
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board(
	int r0, int c0,
	sudoku_board<Rank>& board,
	int depth
) {

	auto reduce_result = board.reduce();
	if(reduce_result == sudoku_reduce_result::success) {
		return true;
	} else if(reduce_result == sudoku_reduce_result::failure) {
		return false;
	}

	if(depth < 22) {
		board.print(std::cout) << std::endl;
	}

	const int d = board.side();

	for(int r = r0; r < d; ++r) {
		for(int c = c0; c < d; ++c) {

			sudoku_cell& cell = board.cell(r, c);

			if(cell.ambiguous()) {
				for(auto value : cell) {

					sudoku_board<Rank> temp(board);
					temp.cell(r, c).init(value);

					if(solve_board(r, c, temp, depth+1)) {
						board = temp;
						return true;
					}
				}
			}
		}
	}
	return false;
}
//------------------------------------------------------------------------------
#endif // include guard
