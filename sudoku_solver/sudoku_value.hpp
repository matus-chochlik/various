// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_VALUE_HPP
#define SUDOKU_VALUE_HPP

#include <cstdint>
#include <cassert>
#include <string>
#include <iostream>
#include "sudoku_defs.hpp"
//------------------------------------------------------------------------------
class sudoku_value {
private:
	short _value;

	static
	const std::string& _rank_input_symbols(int rank);

	static
	const std::string& _rank_output_symbol(int rank, std::size_t sym, short var);

	static
	short _get_symbol_value(int rank, sudoku_symbol symbol);
public:
	sudoku_value(void) noexcept
	 : _value(-1)
	{ }

	explicit
	sudoku_value(std::uint64_t value) noexcept
	 : _value(short(value))
	{ }

	sudoku_value(int rank, sudoku_symbol symbol) noexcept
	 : _value(_get_symbol_value(rank, symbol))
	{ }

	explicit
	operator bool (void) const noexcept {
		return _value >= 0;
	}

	bool operator ! (void) const noexcept {
		return _value < 0;
	}

	friend
	bool operator == (sudoku_value l, sudoku_value r) noexcept {
		return l._value == r._value;
	}

	friend
	bool operator != (sudoku_value l, sudoku_value r) noexcept {
		return l._value != r._value;
	}

	friend
	bool operator <  (sudoku_value l, sudoku_value r) noexcept {
		return l._value <  r._value;
	}

	auto index(void) const {
		assert(_value >= 0);
		return std::uint64_t(_value);
	}

	std::ostream& write_to(std::ostream& out, int rank, short variant) const;
};
//------------------------------------------------------------------------------
inline
const std::string& sudoku_value::_rank_input_symbols(int rank) {

	static const std::string _symbols[7] = {
		{}, {"1"},
		{"1234"},
		{"123456789"},
		{"0123456789ABCDEF"},
		{"ABCDEFGHIJKLMNOPQRSTUVWXY"},
		{"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
	};

	static const int n = int(sizeof(_symbols)/sizeof(_symbols[0]));

	if((rank >= 0) && (rank < n)) {
		return _symbols[rank];
	}
	return _symbols[0];
}
//------------------------------------------------------------------------------
inline
const std::string& sudoku_value::_rank_output_symbol(
	int rank,
	std::size_t sym,
	short variant
) {

	if(rank == 2 && sym < 2*2) {
		if(variant == 1) {
			static const std::string symbols[3*3] = {
				{"\u25F0"},{"\u25F1"},
				{"\u25F2"},{"\u25F3"}
			};
			return symbols[sym];
		}
		if(variant == 2) {
			static const std::string symbols[3*3] = {
				{"\u25F4"},{"\u25F5"},
				{"\u25F6"},{"\u25F7"}
			};
			return symbols[sym];
		}
		if(variant == 3) {
			static const std::string symbols[3*3] = {
				{"\u2680"},{"\u2681"},
				{"\u2682"},{"\u2683"}
			};
			return symbols[sym];
		}
		static const std::string symbols[2*2] = {
			{"1"},{"2"},
			{"3"},{"4"}
		};
		return symbols[sym];
	}
	if(rank == 3 && sym < 3*3) {
		if(variant == 1) {
			static const std::string symbols[3*3] = {
				{"\u25A0"},{"\u25A1"},{"\u25A3"},
				{"\u25A4"},{"\u25A5"},{"\u25A6"},
				{"\u25A7"},{"\u25A8"},{"\u25A9"}
			};
			return symbols[sym];
		}
		if(variant == 2) {
			static const std::string symbols[3*3] = {
				{"\u2295"},{"\u2296"},{"\u2297"},
				{"\u2298"},{"\u2299"},{"\u229A"},
				{"\u229B"},{"\u229C"},{"\u229D"}
			};
			return symbols[sym];
		}
		if(variant == 3) {
			static const std::string symbols[3*3] = {
				{"\u278A"},{"\u278B"},{"\u278C"},
				{"\u278D"},{"\u278E"},{"\u278F"},
				{"\u2790"},{"\u2791"},{"\u2792"}
			};
			return symbols[sym];
		}
		static const std::string symbols[3*3] = {
			{"1"},{"2"},{"3"},
			{"4"},{"5"},{"6"},
			{"7"},{"8"},{"9"}
		};
		return symbols[sym];
	}
	if(rank == 4 && sym < 4*4) {
		if(variant == 1) {
			static const std::string symbols[4*4] = {
				{"\u2735"},{"\u273A"},{"\u273D"},{"\u273F"},
				{"\u2740"},{"\u2742"},{"\u2744"},{"\u2746"},
				{"\u2748"},{"\u2732"},{"\u272D"},{"\u273E"},
				{"\u2731"},{"\u2738"},{"\u2743"},{"\u2736"}
			};
			return symbols[sym];
		}
		static const std::string symbols[4*4] = {
			{"0"},{"1"},{"2"},{"3"},
			{"4"},{"5"},{"6"},{"7"},
			{"8"},{"9"},{"A"},{"B"},
			{"C"},{"D"},{"E"},{"F"}
		};
		return symbols[sym];
	}
	if(rank == 5 && sym < 5*5) {
		static const std::string symbols[5*5] = {
			{"A"},{"B"},{"C"},{"D"},{"E"},
			{"F"},{"G"},{"H"},{"I"},{"J"},
			{"K"},{"L"},{"M"},{"N"},{"O"},
			{"P"},{"Q"},{"R"},{"S"},{"T"},
			{"U"},{"V"},{"W"},{"X"},{"Y"}
		};
		return symbols[sym];
	}
	static const std::string fallback("?");
	return fallback;
}
//------------------------------------------------------------------------------
inline
short sudoku_value::_get_symbol_value(int rank, sudoku_symbol symbol) {

	const auto p = _rank_input_symbols(rank).find(symbol);

	if(p != std::string::npos) {
		return short(p);
	}
	return -1;
}
//------------------------------------------------------------------------------
inline
std::ostream& sudoku_value::write_to(std::ostream& out, int rank, short variant) const {
	if(_value < 0) {
		out << '.';
	} else {
		out << _rank_output_symbol(rank, std::size_t(_value), variant);
	}
	return out;
}
//------------------------------------------------------------------------------
#endif // include guard
