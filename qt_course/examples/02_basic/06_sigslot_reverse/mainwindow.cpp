#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "rev_value.h"

MainWindow::MainWindow(QWidget *parent)
 : QMainWindow(parent)
 , ui(new Ui::MainWindow)
{
	ui->setupUi(this);
	RevValue* rev_val = new RevValue(this);
	connect(
		ui->closeButton,
		SIGNAL(clicked()),
		this,
		SLOT(close())
	);
	connect(
		ui->horizontalSlider,
		SIGNAL(valueChanged(int)),
		rev_val,
		SLOT(setValue(int))
	);
	connect(
		rev_val,
		SIGNAL(valueChanged(int)),
		ui->progressBar,
		SLOT(setValue(int))
	);
	ui->horizontalSlider->setValue(50);
}

MainWindow::~MainWindow()
{
	delete ui;
}
