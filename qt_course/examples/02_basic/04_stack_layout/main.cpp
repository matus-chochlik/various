#include <QApplication>
// widgets
#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>
#include <QCheckBox>
#include <QSpinBox>
// stacked layout
#include <QStackedLayout>
#include <QHBoxLayout>
#include <QVBoxLayout>
// atoi
#include <cstdlib>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	QWidget win;

	QVBoxLayout* vboxLayout = new QVBoxLayout();
	vboxLayout->addSpacing(4);

	QStackedLayout* mainLayout = new QStackedLayout();

	mainLayout->addWidget(new QLabel("Label", &win));
	mainLayout->addWidget(new QPushButton("Button", &win));
	mainLayout->addWidget(new QCheckBox("CheckBox", &win));
	mainLayout->addWidget(new QTextEdit("Text", &win));
	mainLayout->addWidget(new QSpinBox(&win));

	int index = argc<2?0:std::atoi(argv[1]);
	mainLayout->setCurrentIndex(index%5);

	vboxLayout->addLayout(mainLayout);
	vboxLayout->addSpacing(4);

	win.setLayout(vboxLayout);
	win.show();

	return a.exec();
}
