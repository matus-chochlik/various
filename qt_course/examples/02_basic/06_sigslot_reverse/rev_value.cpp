#include "rev_value.h"

void RevValue::setValue(int val)
{
	emit valueChanged(_min+_max-val);
}

RevValue::RevValue(QObject* parent, int min, int max)
 : QObject(parent)
 , _min(min)
 , _max(max)
{ }

