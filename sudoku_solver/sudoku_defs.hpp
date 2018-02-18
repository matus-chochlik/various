// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_DEFS_HPP
#define SUDOKU_DEFS_HPP

using sudoku_symbol = char;

struct sudoku_options
{
	bool sort_cells;
	bool randomize_cells;
	bool print_backtrace;
	bool pango_markup;

	sudoku_options(void)
	 : sort_cells(true)
	 , randomize_cells(false)
	 , print_backtrace(true)
	 , pango_markup(false)
	{ }
};

#endif // include guard
