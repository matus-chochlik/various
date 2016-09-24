#include <QApplication>
// widgets
#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>
#include <QCheckBox>
#include <QStatusBar>
// grid layout
#include <QGridLayout>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	QWidget win;

	QGridLayout* mainLayout = new QGridLayout();

	mainLayout->addWidget(new QLabel("Label11", &win), 0, 0);
	mainLayout->addWidget(new QLabel("Label12", &win), 0, 1);
	mainLayout->addWidget(new QLabel("Label13", &win), 0, 2);

	mainLayout->addWidget(new QLabel("Label21", &win), 1, 0);
	mainLayout->addWidget(new QPushButton("Button22", &win), 1, 1);
	mainLayout->addWidget(new QCheckBox("CheckBox23", &win), 1, 2);

	mainLayout->addWidget(new QLabel("Label31", &win), 2, 0);
	mainLayout->addWidget(new QPushButton("Button32", &win), 2, 1);
	mainLayout->addWidget(new QTextEdit("Edit33", &win), 2, 2);

	mainLayout->setRowStretch(0, 0);
	mainLayout->setRowStretch(1, 1);
	mainLayout->setRowStretch(2, 2);

	mainLayout->setColumnStretch(0, 0);
	mainLayout->setColumnStretch(1, 1);
	mainLayout->setColumnStretch(2, 2);
	win.setLayout(mainLayout);
	win.show();

	return a.exec();
}
