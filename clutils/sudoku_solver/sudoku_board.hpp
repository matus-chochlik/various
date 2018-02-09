// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_BOARD_HPP
#define SUDOKU_BOARD_HPP

#include <iomanip>
#include "sudoku_cell.hpp"
//------------------------------------------------------------------------------
enum class sudoku_reduce_result {
	success,
	partial,
	failure
};
//------------------------------------------------------------------------------
template <int Rank>
class sudoku_board {
private:
	sudoku_cell _cells[Rank*Rank][Rank*Rank];
public:
	sudoku_board(void) = default;

	constexpr int side(void) const noexcept { return Rank*Rank; }

	const sudoku_cell& cell(int r, int c) const { return _cells[r][c]; }
	sudoku_cell& cell(int r, int c) { return _cells[r][c]; }

	sudoku_cell valid_numbers(int r, int c, sudoku_cell v);

	sudoku_cell valid_numbers(int r, int c) {
		return valid_numbers(r, c, sudoku_cell::all_options(Rank));
	}

	void read(std::istream& input);

	std::ostream& print(std::ostream& output);

	std::ostream& print_counts(std::ostream& output);

	sudoku_reduce_result reduce(void);
};
//------------------------------------------------------------------------------
template <int Rank>
sudoku_cell sudoku_board<Rank>::valid_numbers(int r, int c, sudoku_cell v) {
	const int d = side();
	const int k = Rank;

	for(int x = 0; x < d; ++x) {
		sudoku_cell& cr = cell(r, x);

		if((x != c) && cr.determined()) {
			v.remove(cr.value());
		}
	}

	for(int y = 0; y < d; ++y) {
		sudoku_cell& cr = cell(y, c);

		if((y != r) && cr.determined()) {
			v.remove(cr.value());
		}
	}

	for(int y = (r/k)*k; y < (1+r/k)*k; ++y) {
		for(int x = (c/k)*k; x < (1+c/k)*k; ++x) {

			if((y != r) && (x != c)) {
				sudoku_cell& cr = cell(y, x);
				if(cr.determined()) {
					v.remove(cr.value());
				}
			}
		}
	}

	return v;
}
//------------------------------------------------------------------------------
template <int Rank>
void sudoku_board<Rank>::read(std::istream& input) {
	const int d = side();

	char v, s;
	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			v = input.get();
			s = input.get();

			cell(r, c).init(sudoku_value(Rank, v));

			if((s == '\n') && (c < (d - 1))) {
				throw std::runtime_error("Line too short");
			} else if((s != ' ') && (s != '\t') && (s != '\n')) {
				throw std::runtime_error("Invalid separator");
			}
		}

		if(s != '\n') {
			throw std::runtime_error("Line too long");
		}
	}

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			if(!cell(r, c).determined()) {
				cell(r, c) = valid_numbers(r, c);
			}
		}
	}
}
//------------------------------------------------------------------------------
template <int Rank>
std::ostream& sudoku_board<Rank>::print(std::ostream& output) {
	const int d = side();

	for(int r = 0; r < d; ++r) {
		if((r > 0) && (r % Rank == 0)) {
			for(int c = 0; c < d; ++c) {
				if((c + 1) == d) {
					std::cout << "-";
				} else if((c + 1) % Rank == 0) {
					std::cout << "-+";
				} else {
					std::cout << "--";
				}
			}
			std::cout << std::endl;
		}

		for(int c = 0; c < d; ++c) {

			const auto& cl = cell(r, c);

			if(cl.determined()) {
				cl.value().write_to(std::cout, Rank);
			} else if(cl.empty()) {
					std::cout << '.';
			} else {
					std::cout << '?';
			}

			if((c + 1) < d) {
				if((c + 1) % Rank == 0) {
					std::cout << "|";
				} else {
					std::cout << " ";
				}
			} else {
				std::cout << std::endl;
			}
		}
	}
	return output;
}
//------------------------------------------------------------------------------
template <int Rank>
std::ostream& sudoku_board<Rank>::print_counts(std::ostream& output) {
	const int d = side();

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {

			const auto& cl = cell(r, c);

			std::cout << std::setfill(' ');
			std::cout << std::setw(4);
			std::cout << cl.num_options();

			if((c + 1) < d) {
				std::cout << " ";
			} else {
				std::cout << std::endl;
			}
		}
	}
	return output;
}
//------------------------------------------------------------------------------
template <int Rank>
sudoku_reduce_result sudoku_board<Rank>::reduce(void) {
	const int d = side();

	while(true) {
		int solved = 0;
		int unsolved = 0;

		for(int r=0; r<d; ++r) {
			for(int c=0; c<d; ++c) {
				sudoku_cell& candidate = cell(r, c);
				if(!candidate.determined()) {
					candidate = valid_numbers(r, c, std::move(candidate));

					if(candidate.empty()) {
						return sudoku_reduce_result::failure;
					}

					if(candidate.determined()) {
						++solved;
					} else {
						++unsolved;
					}
				}
			}
		}
		if(!unsolved) return sudoku_reduce_result::success;
		if(!solved) break;
	}
	return sudoku_reduce_result::partial;
}
//------------------------------------------------------------------------------
#endif // include guard
