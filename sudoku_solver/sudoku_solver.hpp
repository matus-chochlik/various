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

	std::ostream& print(std::ostream& output, const sudoku_options& options) {
		return _board.print(output, options);
	}

	std::ostream& print_counts(std::ostream& output) {
		return _board.print_counts(output);
	}

	static bool solve_board(
		sudoku_board<Rank>& b,
		int r0, int c0,
		const sudoku_options& options
	);

	bool solve(const sudoku_options& options) {
		return solve_board(_board, 0, 0, options);
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board(
	sudoku_board<Rank>& board,
	int r0, int c0,
	const sudoku_options& options
) {
	board.print(std::cout, options) << std::endl;

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

					if(solve_board(fixed_board, r, c, options)) {
						board = fixed_board;
						return true;
					}
				}
				if(options.print_backtrace) {
					board.print(std::cout, options) << std::endl;
				}
				return false;
			}
		}
	}
	return false;
}
//------------------------------------------------------------------------------
#endif // include guard
