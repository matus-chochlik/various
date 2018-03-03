// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_SOLVER_HPP
#define SUDOKU_SOLVER_HPP

#include <random>
#include <algorithm>
#include "sudoku_board.hpp"
//------------------------------------------------------------------------------
template <int Rank>
class sudoku_solver {
private:
	sudoku_board<Rank> _board;
	std::default_random_engine _rand;
public:
	sudoku_solver(void)
	 : _rand(std::random_device()())
	{ }

	void read(std::istream& input) {
		_board.read(input);
	}

	std::ostream& print(std::ostream& output, const sudoku_options& options) {
		return _board.print(output, options);
	}

	std::ostream& print_counts(std::ostream& output) {
		return _board.print_counts(output);
	}

	bool solve_board(
		sudoku_board<Rank>& b,
		const sudoku_options& options
	);

	bool solve(const sudoku_options& options) {
		return solve_board(_board, options);
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board(
	sudoku_board<Rank>& board,
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
	const auto n = d*d;

	using component_t = std::int8_t;
	using coord = std::pair<component_t, component_t>;
	coord index[n];

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			index[r*d+c] = coord(component_t(r), component_t(c));
		}
	}

	const auto e = std::remove_if(
		index, index + n,
		[&board](const coord& i) {
			return board.cell(i.first, i.second).is_determined();
		}
	);

	if(options.randomize_cells) {
		std::shuffle(index, e, _rand);
	}

	if(options.sort_cells) {
		std::sort(
			index, e,
			[&board](const coord& i, const coord& j) {
				return	board.cell(i.first, i.second).num_options()<
						board.cell(j.first, j.second).num_options();
			}
		);
	}

	if(options.depth_first) {
		for(auto p = index; p < e; ++p) {
			int r = p->first;
			int c = p->second;

			const sudoku_cell& cell = board.cell(r, c);
			assert(cell.is_ambiguous());

			for(auto value : cell) {

				sudoku_board<Rank> fixed_board(board);
				fixed_board.cell(r, c).init(value);

				if(solve_board(fixed_board, options)) {
					board = fixed_board;
					return true;
				}
			}
			if(options.print_backtrace) {
				board.print(std::cout, options) << std::endl;
			}
			return false;
		}
	} else {
		while(true) {
			for(auto p = index; p < e; ++p) {
				int r = p->first;
				int c = p->second;

				sudoku_cell& cell = board.cell(r, c);

				if(auto value = cell.value()) {

					sudoku_board<Rank> fixed_board(board);
					fixed_board.cell(r, c).init(value);

					if(solve_board(fixed_board, options)) {
						board = fixed_board;
						return true;
					}
					if(options.print_backtrace) {
						board.print(std::cout, options) << std::endl;
					}
					cell.remove(value);

					if(cell.is_empty()) {
						return false;
					}
				} else {
					return false;
				}
			}
		}
	}
	return false;
}
//------------------------------------------------------------------------------
#endif // include guard
