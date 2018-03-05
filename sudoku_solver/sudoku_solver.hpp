// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_SOLVER_HPP
#define SUDOKU_SOLVER_HPP

#include <tuple>
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

	bool solve_board_depth(
		sudoku_board<Rank>& b,
		const sudoku_options& options
	);

	bool solve_board_breadth(
		sudoku_board<Rank>& b,
		const sudoku_options& options
	);

	bool solve(const sudoku_options& options) {
		if(options.depth_first) {
			return solve_board_depth(_board, options);
		} else {
			return solve_board_breadth(_board, options);
		}
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board_depth(
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
	using coord = std::tuple<component_t, component_t>;
	using std::get;
	coord index[n];

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			index[r*d+c] = coord(component_t(r), component_t(c));
		}
	}

	const auto e = std::remove_if(
		std::begin(index), std::end(index),
		[&board](const coord& i) {
			return board.cell(get<0>(i), get<1>(i)).is_determined();
		}
	);

	if(options.randomize_cells) {
		std::shuffle(std::begin(index), e, _rand);
	}

	if(options.sort_cells) {
		std::sort(
			std::begin(index), e,
			[&board](const coord& i, const coord& j) {
				return	board.cell(get<0>(i), get<1>(i)).num_options()<
						board.cell(get<0>(j), get<1>(j)).num_options();
			}
		);
	}

	for(auto p = std::begin(index); p < e; ++p) {
		int r = get<0>(*p);
		int c = get<1>(*p);

		const sudoku_cell& cell = board.cell(r, c);
		assert(cell.is_ambiguous());

		for(auto value : cell) {

			sudoku_board<Rank> fixed_board(board);
			fixed_board.cell(r, c).init(value);

			if(solve_board_depth(fixed_board, options)) {
				board = fixed_board;
				return true;
			}
		}
		if(options.print_backtrace) {
			board.print(std::cout, options) << std::endl;
		}
		return false;
	}
	return false;
}
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board_breadth(
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
	using coord = std::tuple<component_t, component_t, sudoku_cell::iterator>;
	using std::get;

	std::vector<coord> index(n);

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			index[r*d+c] = coord(
				component_t(r),
				component_t(c),
				board.cell(r, c).begin()
			);
		}
	}

	const auto e = index.erase(
		std::remove_if(
			std::begin(index), std::end(index),
			[&board](const coord& i) {
				return board.cell(get<0>(i), get<1>(i)).is_determined();
			}
		), index.end()
	);

	if(options.randomize_cells) {
		std::shuffle(std::begin(index), e, _rand);
	}

	if(options.sort_cells) {
		std::sort(
			std::begin(index), e,
			[&board](const coord& i, const coord& j) {
				return	board.cell(get<0>(i), get<1>(i)).num_options()<
						board.cell(get<0>(j), get<1>(j)).num_options();
			}
		);
	}

	while(true) {
		bool done_something = false;
		for(auto p = std::begin(index); p < e; ++p) {
			int r = get<0>(*p);
			int c = get<1>(*p);

			const sudoku_cell& cell = board.cell(r, c);
			assert(cell.is_ambiguous());

			auto& iter = get<2>(*p);

			if(iter != cell.end()) {

				const auto value = *iter;

				sudoku_board<Rank> fixed_board(board);
				fixed_board.cell(r, c).init(value);

				if(solve_board_breadth(fixed_board, options)) {
					board = fixed_board;
					return true;
				}
				++iter;
				done_something = true;
			}
			if(options.print_backtrace) {
				board.print(std::cout, options) << std::endl;
			}
		}
		if(!done_something) {
			break;
		}
	}
	return false;
}
//------------------------------------------------------------------------------
#endif // include guard
