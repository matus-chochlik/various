// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_DEFS_HPP
#define SUDOKU_DEFS_HPP

using sudoku_symbol = char;

struct sudoku_options
{
	short variant;
	bool depth_first;
	bool sort_cells;
	bool randomize_cells;
	bool print_metadata;
	bool print_fancy;
	bool pango_markup;
	bool print_backtrace;

	sudoku_options(void)
	 : variant(0)
	 , depth_first(true)
	 , sort_cells(true)
	 , randomize_cells(false)
	 , print_metadata(true)
	 , print_fancy(false)
	 , pango_markup(false)
	 , print_backtrace(true)
	{ }
};

#endif // include guard
