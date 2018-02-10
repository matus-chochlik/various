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

	class shuffler {
	private:
		int _idx[Rank*Rank][Rank*Rank];
	public:
		shuffler(void) {
			std::random_device rd;
			std::default_random_engine re(rd());

			for(int r=0; r<Rank*Rank; ++r) {
				for(int c=0; c<Rank*Rank; ++c) {
					_idx[r][c] = c;
				}
				std::shuffle(_idx[r], _idx[r]+Rank*Rank, re);
			}
		}

		int get(int i) const {
			return _idx[Rank][i];
		}

		int get(int r, int c) const {
			return _idx[r][c];
		}
	};

	static bool solve_board(
		sudoku_board<Rank>& b,
		const shuffler& shfl,
		int depth
	);

	bool solve(void) {
		shuffler shfl;
		return solve_board(_board, shfl, 0);
	}
};
//------------------------------------------------------------------------------
template <int Rank>
inline bool sudoku_solver<Rank>::solve_board(
	sudoku_board<Rank>& board,
	const shuffler& shfl,
	int depth
) {
	auto reduce_result = board.reduce();

	if(reduce_result == sudoku_reduce_result::success) {
		return true;
	} else if(reduce_result == sudoku_reduce_result::failure) {
		return false;
	}

	board.print(std::cout) << std::endl;

	const int d = board.side();

	for(int ri = 0; ri < d; ++ri) {
		for(int ci = 0; ci < d; ++ci) {

			const int r = shfl.get(ri);
			const int c = shfl.get(ri, ci);

			const sudoku_cell& cell = board.cell(r, c);

			if(cell.is_ambiguous()) {
				for(auto value : cell) {

					sudoku_board<Rank> fixed_board(board);
					fixed_board.cell(r, c).init(value);

					bool solved = false;
					if(depth % 3 == 0) {
						shuffler shfl2;
						solved = solve_board(fixed_board, shfl2, depth+1);
					} else {
						solved = solve_board(fixed_board, shfl, depth+1);
					}

					if(solved) {
						board = fixed_board;
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
