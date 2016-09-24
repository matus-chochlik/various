#include <QApplication>
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QPixmap>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	QWidget win;

	QVBoxLayout* mainLayout = new QVBoxLayout(&win);

	// button
	QPushButton* closeButton = new QPushButton("Close", &win);

	QPixmap closePixmap(":/icon-close.png");
	QIcon closeIcon(closePixmap);
	closeButton->setIcon(closeIcon);
	closeButton->setIconSize(QSize(64, 64));
	mainLayout->addWidget(closeButton, 1, Qt::AlignCenter);

	QObject::connect(closeButton, SIGNAL(clicked()), &win, SLOT(close()));

	win.resize(200, 100);
	win.show();

	return a.exec();
}
