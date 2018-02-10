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

	static bool solve_board(sudoku_board<Rank>& b, int r0, int c0);

	bool solve(void) {
		return solve_board(_board, 0, 0);
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board(
	sudoku_board<Rank>& board,
	int r0, int c0
) {
	board.print(std::cout) << std::endl;

	auto reduce_result = board.reduce();

	if(reduce_result == sudoku_reduce_result::success) {
		return true;
	} else if(reduce_result == sudoku_reduce_result::failure) {
		return false;
	}

	const int d = board.side();

	for(int r = r0; r < d; ++r) {
		for(int c = (r == r0) ? c0 : 0; c < d; ++c) {

			const sudoku_cell& cell = board.cell(r, c);

			if(cell.is_ambiguous()) {

				for(auto value : cell) {

					sudoku_board<Rank> fixed_board(board);
					fixed_board.cell(r, c).init(value);

					if(solve_board(fixed_board, r, c)) {
						board = fixed_board;
						return true;
					}
				}
				board.print(std::cout) << std::endl;
				return false;
			}
		}
	}
	return false;
}
//------------------------------------------------------------------------------
#endif // include guard
