/* Copyright (c) 2016 Matus Chochlik
 */
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <set>
#include <memory>
#include <cassert>

class sudoku_cell
{
public:
	typedef uint8_t value_t;
private:
	std::set<value_t> _values;

	sudoku_cell(std::set<value_t> values)
	 : _values(std::move(values))
	{ }
public:
	sudoku_cell(void) = default;

	static sudoku_cell all_options(void)
	{
		return {{5,3,7,2,4,1,6,8,9}};
	}

	bool empty(void) const
	{
		return _values.empty();
	}

	bool ambiguous(void) const
	{
		return _values.size() > 1;
	}

	bool determined(void) const
	{
		return !(empty() || ambiguous());
	}

	value_t single_number(void) const
	{
		assert(determined());
		return *_values.begin();
	}

	void remove(value_t v)
	{
		_values.erase(v);
	}

	void clear(void)
	{
		_values.clear();
	}

	void init(value_t v)
	{
		if(!_values.empty()) clear();
		_values.insert(v);
	}

	auto begin(void) const
	{
		return _values.begin();
	}

	auto end(void) const
	{
		return _values.end();
	}
};

class sudoku_board
{
public:
	typedef sudoku_cell::value_t value_t;
private:
	sudoku_cell _cells[9][9];
public:
	const sudoku_cell& cell(int r, int c) const
	{
		return _cells[r][c];
	}

	sudoku_cell& cell(int r, int c)
	{
		return _cells[r][c];
	}

	sudoku_cell valid_numbers(int r, int c, sudoku_cell v);

	sudoku_cell valid_numbers(int r, int c)
	{
		return valid_numbers(r, c, sudoku_cell::all_options());
	}

	void read(std::istream& input);

	void print(std::ostream& output);

	bool reduce(void);
};

class sudoku_solver
{
public:
	typedef sudoku_board::value_t value_t;
private:
	sudoku_board _board;
public:
	void read(std::istream& input)
	{
		_board.read(input);
	}

	void print(std::ostream& output)
	{
		_board.print(output);
	}

	static bool solve_board(int r0, int c0, sudoku_board& b);

	bool solve(void)
	{
		return solve_board(0, 0, _board);
	}
};

int main(void)
{
	sudoku_solver s;
	s.read(std::cin);

	if(s.solve()) s.print(std::cout);
	else std::cout << "cannot solve this board!" << std::endl;

	return 0;
}

sudoku_cell sudoku_board::valid_numbers(int r, int c, sudoku_cell v)
{
	for(int x=0; x<9; ++x)
	{
		sudoku_cell& cr = cell(r, x);
		if((x != c) && cr.determined())
		{
			v.remove(cr.single_number());
		}
	}
	for(int y=0; y<9; ++y)
	{
		sudoku_cell& cr = cell(y, c);
		if((y != r) && cr.determined())
		{
			v.remove(cr.single_number());
		}
	}
	for(int y=(r/3)*3; y<(1+r/3)*3; ++y)
	{
		for(int x=(c/3)*3; x<(1+c/3)*3; ++x)
		{
			if((y != r) && (x != c))
			{
				sudoku_cell& cr = cell(y, x);
				if(cr.determined())
				{
					v.remove(cr.single_number());
				}
			}
		}
	}
	return v;
}

void sudoku_board::read(std::istream& input)
{
	char v, s;
	for(int r=0; r<9; ++r)
	{
		for(int c=0; c<9; ++c)
		{
			v = input.get();
			s = input.get();
			if(('1' <= v) && (v <= '9'))
			{
				cell(r, c).init(v-'0');
			}
			else
			{
				cell(r, c).clear();
			}

			if((s == '\n') && (c < 8))
			{
				throw std::runtime_error("Line too short");
			}
			else if((s != ' ') && (s != '\t') && (s != '\n'))
			{
				throw std::runtime_error("Invalid separator");
			}
		}
		if(s != '\n')
		{
			throw std::runtime_error("Line too long");
		}
	}
	for(int r=0; r<9; ++r)
	{
		for(int c=0; c<9; ++c)
		{
			if(!cell(r, c).determined())
			{
				cell(r, c) = valid_numbers(r, c);
			}
		}
	}
}

void sudoku_board::print(std::ostream& output)
{
	for(int r=0; r<9; ++r)
	{
		for(int c=0; c<9; ++c)
		{
			unsigned v = 0;
			for(auto n : cell(r, c))
			{
				v *= 10;
				v += n;
			}
			std::cout << std::setfill(' ');
			std::cout << std::setw(10);
			std::cout << v;
			if(c < 8) std::cout << " ";
			else std::cout << std::endl;
		}
	}
}

bool sudoku_board::reduce(void)
{
	while(true)
	{
		int solved = 0;
		int unsolved = 0;

		for(int r=0; r<9; ++r)
		{
			for(int c=0; c<9; ++c)
			{
				sudoku_cell& cr = cell(r, c);
				if(!cr.determined())
				{
					cr = valid_numbers(r, c, std::move(cr));

					if(cr.determined())
					{
						++solved;
					}
					else
					{
						++unsolved;
					}
				}
			}
		}
		if(!unsolved) return true;
		if(!solved) break; 
	}
	return false;
}

bool sudoku_solver::solve_board(int r0, int c0, sudoku_board& b)
{
	if(b.reduce()) return true;

	for(int r=r0; r<9; ++r)
	for(int c=c0; c<9; ++c)
	{
		sudoku_cell& cr = b.cell(r, c);
		if(cr.ambiguous())
		{
			for(auto v : cr)
			{
				sudoku_board n(b);
				n.cell(r, c).init(v);
				if(solve_board(r, c, n))
				{
					b = n;
					return true;
				}
			}
		}
	}
	return false;
}

