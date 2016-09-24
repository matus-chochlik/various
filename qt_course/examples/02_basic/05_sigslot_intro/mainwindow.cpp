#include "mainwindow.h"
#include "ui_mainwindow.h"

MainWindow::MainWindow(QWidget *parent)
 : QMainWindow(parent)
 , ui(new Ui::MainWindow)
{
	ui->setupUi(this);
	connect(
		ui->closeButton,
		SIGNAL(clicked()),
		this,
		SLOT(close())
	);
	connect(
		ui->horizontalSlider,
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
