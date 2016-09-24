#include <QApplication>
// widgets
#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>
#include <QCheckBox>
#include <QStatusBar>
// box layouts
#include <QVBoxLayout>
#include <QHBoxLayout>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	QWidget win;

	QVBoxLayout* mainLayout = new QVBoxLayout();

	// first row
	QHBoxLayout* firstRowLayout = new QHBoxLayout();
	firstRowLayout->addWidget(new QLabel("Label1", &win), 0);
	firstRowLayout->addWidget(new QCheckBox("Flip me", &win), 2);
	firstRowLayout->addWidget(new QPushButton("Push me", &win), 1);
	mainLayout->addLayout(firstRowLayout, 0);
	//
	// second row
	QHBoxLayout* secondRowLayout = new QHBoxLayout();
	secondRowLayout->addWidget(new QLabel("Label2", &win), 0);
	secondRowLayout->addWidget(new QTextEdit("Edit me", &win), 1);
	mainLayout->addLayout(secondRowLayout, 0);

	// button
	QPushButton* clickButton = new QPushButton("Click me", &win);
	mainLayout->addWidget(clickButton, 0, Qt::AlignCenter);

	// status bar
	QStatusBar* statusBar = new QStatusBar(&win);
	statusBar->showMessage("Status text");
	mainLayout->addWidget(statusBar, 0);

	win.setLayout(mainLayout);
	win.show();

	return a.exec();
}
