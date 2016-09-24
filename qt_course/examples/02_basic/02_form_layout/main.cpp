#include <QApplication>
// widgets
#include <QWidget>
#include <QPushButton>
#include <QLabel>
#include <QTextEdit>
#include <QCheckBox>
#include <QSpinBox>
// form layout
#include <QFormLayout>

int main(int argc, char *argv[])
{
	QApplication a(argc, argv);
	QWidget win;

	QFormLayout* mainLayout = new QFormLayout();

	mainLayout->addRow("Item1", new QLabel("Label", &win));
	mainLayout->addRow("Item2", new QCheckBox("Checkbox", &win));
	mainLayout->addRow("Item3", new QPushButton("Button", &win));
	mainLayout->addRow("Item4", new QTextEdit("Text", &win));
	mainLayout->addRow("Item5", new QSpinBox(&win));

	win.setLayout(mainLayout);
	win.show();

	return a.exec();
}
