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
	const std::string& _rank_output_symbols(int rank);

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

	std::ostream& write_to(std::ostream& out, int rank) const;
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
const std::string& sudoku_value::_rank_output_symbols(int rank) {

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
short sudoku_value::_get_symbol_value(int rank, sudoku_symbol symbol) {

	const auto p = _rank_input_symbols(rank).find(symbol);

	if(p != std::string::npos) {
		return short(p);
	}
	return -1;
}
//------------------------------------------------------------------------------
inline
std::ostream& sudoku_value::write_to(std::ostream& out, int rank) const {
	if(_value < 0) {
		out << '.';
	} else {
		const std::size_t index(_value);
		assert(index < _rank_output_symbols(rank).size());
		out << _rank_output_symbols(rank)[index];
	}
	return out;
}
//------------------------------------------------------------------------------
#endif // include guard
