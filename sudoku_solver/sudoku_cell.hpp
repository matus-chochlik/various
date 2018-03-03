// Copyright (c) 2016 -2018 Matus Chochlik
//
#ifndef SUDOKU_CELL_HPP
#define SUDOKU_CELL_HPP

#include <cstdint>
#include <cassert>
#include <utility>
#include "sudoku_value.hpp"
//------------------------------------------------------------------------------
class sudoku_cell {
public:
	static constexpr std::size_t capacity = 64;
	using container_t = std::uint64_t ;
	using flags_t = std::uint8_t ;
private:
	container_t _values;
	flags_t _flags;

	static container_t _bit(std::size_t index) noexcept {
		return container_t{1} << index;
	}

	sudoku_cell(container_t values)
	 : _values(values)
	 , _flags{0}
	{ }

	static sudoku_cell make_all_options(int rank);

	template <std::size_t ... I>
	static sudoku_cell get_all_options(int rank, std::index_sequence<I...>);
public:
	enum class flags : flags_t {
		initial = 0x1
	};

	sudoku_cell(void)
	 : _values{0}
	 , _flags{0}
	{ }

	static sudoku_cell all_options(int rank);

	friend bool operator == (const sudoku_cell& a, const sudoku_cell& b)
	{
		return a._values == b._values;
	}

	friend bool operator != (const sudoku_cell& a, const sudoku_cell& b)
	{
		return a._values != b._values;
	}

	bool is_empty(void) const {
		return _values == 0;
	}

	bool is_ambiguous(void) const {
		return (_values & (_values - 1)) != 0;
	}

	bool is_determined(void) const {
		return !(is_empty() || is_ambiguous());
	}

	std::size_t num_options(void) const {
		std::size_t result = 0;
		for(std::size_t i=0; i<capacity; ++i) {
			if((_values & _bit(i)) == _bit(i)) {
				++result;
			}
		}
		return result;
	}

	sudoku_value value(void) const {
		for(std::size_t i=0; i<capacity; ++i) {
			if((_values & _bit(i)) == _bit(i))
				return sudoku_value(i);
		}
		return sudoku_value();
	}

	sudoku_cell& remove(sudoku_value v) {
		assert(v);
		_values &= ~_bit(v.index());
		return *this;
	}

	sudoku_cell& clear(void) {
		_values = 0;
		_flags = 0;
		return *this;
	}

	sudoku_cell& set(container_t v) {
		_values = _bit(v);
		return *this;
	}

	sudoku_cell& init(sudoku_value v) {
		if(v) {
			set(container_t(v.index()));
		} else {
			clear();
		}
		return *this;
	}

	bool is_flag_set(flags flag) const {
		return (_flags & flags_t(flag)) == flags_t(flag);
	}

	sudoku_cell& set_flag(flags flag) {
		_flags |= flags_t(flag);
		return *this;
	}

	sudoku_cell& clear_flag(flags flag) {
		_flags &= ~flags_t(flag);
		return *this;
	}

	bool is_initial(void) const {
		return is_flag_set(flags::initial);
	}

	sudoku_cell& set_initial(void) {
		return set_flag(flags::initial);
	}

	class iterator {
	private:
		container_t _values;
		container_t _index;

		container_t _bit(void) const {
			return sudoku_cell::_bit(_index);
		}

		container_t _tail(void) const {
			return _values >> _index;
		}

		void _find_next(void) {
			while(_index < capacity) {
				const container_t bit = _bit();
				if((_values & bit) == bit) {
					break;
				}
				if(_tail() == 0) {
					_index = capacity;
					break;
				}
				++_index;
			}
		}
	public:
		using value_type = sudoku_value;

		iterator(void)
		 : _values{0}
		 , _index{0}
		{ }

		iterator(container_t values, container_t index)
		 : _values{values}
		 , _index{index}
		{
			_find_next();
		}

		sudoku_value operator * (void) const {
			return sudoku_value(int(_index));
		}

		friend bool operator == (const iterator& l, const iterator& r) {
			return l._index == r._index;
		}

		friend bool operator != (const iterator& l, const iterator& r) {
			return l._index != r._index;
		}

		iterator& operator ++ (void) {
			++_index;
			_find_next();
			return *this;
		}
	};
	friend class iterator;

	auto begin(void) const {
		return iterator(_values, 0);
	}

	auto end(void) const {
		return iterator(_values, capacity);
	}
};
//------------------------------------------------------------------------------
inline
sudoku_cell sudoku_cell::make_all_options(int rank) {
	container_t values = 0;
	const auto n = std::size_t(rank*rank);
	assert(n < capacity);
	for(std::size_t i=0; i<n; ++i) {
		values |= _bit(i);
	}
	return sudoku_cell(values);
}
//------------------------------------------------------------------------------
template <std::size_t ... I>
sudoku_cell sudoku_cell::get_all_options(int rank, std::index_sequence<I...>) {
	static const std::size_t N = sizeof...(I);
	assert((rank > 0) && (rank < int(N)));
	(void)N;

	static sudoku_cell opts[sizeof...(I)] = {make_all_options(int(I))...};

	return opts[rank];
}
//------------------------------------------------------------------------------
inline
sudoku_cell sudoku_cell::all_options(int rank) {
	return get_all_options(rank, std::make_index_sequence<7>());
}
//------------------------------------------------------------------------------
#endif // include guard
