#include <QtGui>
#include <QApplication>
#include <QLabel>

int main(int argc, char* argv[])
{
	QApplication app(argc, argv);
	QLabel label("<I>Hello</I>, <B>GUI</B> world!");
	label.show();
	return app.exec();
}
