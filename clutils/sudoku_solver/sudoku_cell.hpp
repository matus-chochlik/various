// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_CELL_HPP
#define SUDOKU_CELL_HPP

#include <set>
#include <map>
#include <utility>
#include <cassert>
#include "sudoku_value.hpp"
//------------------------------------------------------------------------------
class sudoku_cell {
private:
	std::set<sudoku_value> _values;

	sudoku_cell(std::set<sudoku_value> values)
	 : _values(std::move(values))
	{ }

	static std::set<sudoku_value> make_all_options(int rank);
public:
	sudoku_cell(void) = default;

	static sudoku_cell all_options(int rank);

	bool empty(void) const {
		return _values.empty();
	}

	auto num_options(void) const {
		return _values.size();
	}

	bool ambiguous(void) const {
		return num_options() > 1;
	}

	bool determined(void) const {
		return !(empty() || ambiguous());
	}

	sudoku_value value(void) const {
		assert(determined());
		return *_values.begin();
	}

	void remove(sudoku_value v) {
		_values.erase(v);
	}

	void clear(void) {
		_values.clear();
	}

	void init(sudoku_value v) {
		if(!_values.empty()) clear();
		_values.insert(std::move(v));
	}

	auto begin(void) const {
		return _values.begin();
	}

	auto end(void) const {
		return _values.end();
	}
};
//------------------------------------------------------------------------------
inline
std::set<sudoku_value> sudoku_cell::make_all_options(int rank) {
	std::set<sudoku_value> result;

	for(int i=0; i<rank*rank; ++i) {
		result.insert(i);
	}
	return result;
}
//------------------------------------------------------------------------------
inline
sudoku_cell sudoku_cell::all_options(int rank) {

	static std::map<int, std::set<sudoku_value>> opt_map;

	auto p = opt_map.find(rank);
	if(p == opt_map.end()) {
		p = opt_map.emplace(rank, make_all_options(rank)).first;
	}
	return p->second;
}
//------------------------------------------------------------------------------
#endif // include guard
