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

	std::ostream& print(std::ostream& output, const sudoku_options&);

	std::ostream& print_counts(std::ostream& output);

	sudoku_reduce_result reduce(void);
};
//------------------------------------------------------------------------------
template <int Rank>
sudoku_cell sudoku_board<Rank>::valid_numbers(int r, int c, sudoku_cell v) {
	const int d = side();

	for(int x = 0; x < d; ++x) {
		sudoku_cell& cr = cell(r, x);

		if((x != c) && cr.is_determined()) {
			v.remove(cr.value());
		}
	}

	for(int y = 0; y < d; ++y) {
		sudoku_cell& cr = cell(y, c);

		if((y != r) && cr.is_determined()) {
			v.remove(cr.value());
		}
	}

	for(int y = (r/Rank)*Rank; y < (1+r/Rank)*Rank; ++y) {
		for(int x = (c/Rank)*Rank; x < (1+c/Rank)*Rank; ++x) {

			if((y != r) && (x != c)) {
				sudoku_cell& cr = cell(y, x);
				if(cr.is_determined()) {
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
	for(int r = 0; r < d;) {
		bool sep_row = false;
		for(int c = 0; c < d; ++c) {
			v = input.get();
			s = input.get();

			if(v == '-') {
				if((s != '-') && (s != '+') && (s != '\n')) {
					throw std::runtime_error("Invalid separator");
				}
				sep_row = true;
			} else {
				cell(r, c).init(sudoku_value(Rank, v)).set_initial();

				if((s == '\n') && (c < (d - 1))) {
					throw std::runtime_error("Line too short");
				} else if((s != ' ') && (s != '|') && (s != '\t') && (s != '\n')) {
					throw std::runtime_error("Invalid separator");
				}
			}
		}

		if(s != '\n') {
			throw std::runtime_error("Line too long");
		}

		if(!sep_row) {
			++r;
		}
	}

	for(int r = 0; r < d; ++r) {
		for(int c = 0; c < d; ++c) {
			if(!cell(r, c).is_determined()) {
				cell(r, c) = valid_numbers(r, c);
			}
		}
	}
}
//------------------------------------------------------------------------------
template <int Rank>
std::ostream& sudoku_board<Rank>::print(
	std::ostream& output,
	const sudoku_options& options
) {
	const int d = side();

	for(int c = 0; c < d; ++c) {
		if(c == 0) {
			output << "┏━━";
		} else if((c + 1) == d) {
			output << "━┓";
		} else if((c + 1) % Rank == 0) {
			output << "━┯";
		} else {
			output << "━━";
		}
	}
	output << std::endl;

	for(int r = 0; r < d; ++r) {
		if((r > 0) && (r % Rank == 0)) {
			output << "┠";
			for(int c = 0; c < d; ++c) {
				if((c + 1) == d) {
					if((r + 1) == d) {
						output << "━┛";
					} else {
						output << "─┨";
					}
				} else if((c + 1) % Rank == 0) {
					output << "─┼";
				} else {
					output << "──";
				}
			}
			output << std::endl;
		}

		output << "┃";

		for(int c = 0; c < d; ++c) {

			const auto& cl = cell(r, c);

			if(cl.is_determined()) {
				if(options.pango_markup && cl.is_initial()) {
					output << "<b>";
					cl.value().write_to(output, Rank, options.variant);
					output << "</b>";
				} else {
					cl.value().write_to(output, Rank, options.variant);
				}
			} else if(cl.is_empty()) {
					output << "×";
			} else {
				if(((r + c) % 2) == 0) {
					output << "∴";
				} else {
					output << "∵";
				}
			}

			if((c + 1) < d) {
				if((c + 1) % Rank == 0) {
					output << "│";
				} else {
					output << " ";
				}
			} else {
				output << "┃" << std::endl;
			}
		}
	}

	for(int c = 0; c < d; ++c) {
		if(c == 0) {
			output << "┗━━";
		} else if((c + 1) == d) {
			output << "━┛";
		} else if((c + 1) % Rank == 0) {
			output << "━┷";
		} else {
			output << "━━";
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

			output << std::setfill(' ');
			output << std::setw(4);
			output << cl.num_options();

			if((c + 1) < d) {
				output << " ";
			} else {
				output << std::endl;
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
				if(!candidate.is_determined()) {
					candidate = valid_numbers(r, c, candidate);

					if(candidate.is_empty()) {
						return sudoku_reduce_result::failure;
					}

					if(candidate.is_determined()) {
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
