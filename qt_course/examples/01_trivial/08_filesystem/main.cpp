#include <QDir>
#include <QFile>
#include <QDebug>

void print_dir_info(const QString& title, QDir&& dir)
{
	qDebug() << title;
	qDebug() << "-------------------------------";
	qDebug() << dir.path();
	qDebug() << dir.dirName();
	qDebug() << dir.exists();
	qDebug() << dir.isRoot();

	qDebug() << dir.count() << "entries:";

	dir.setFilter(QDir::NoDotAndDotDot|QDir::Files|QDir::Dirs);
	dir.setSorting(QDir::DirsFirst|QDir::Name);
	QFileInfoList entries = dir.entryInfoList();

	for(QFileInfo info : entries)
	{
		const char* kind = "other";
		if(info.isDir()) kind = "dir";
		else if(info.isFile()) kind = "file";

		qDebug() << "  " << kind << info.completeBaseName();
	}
	qDebug() << "-------------------------------";
}
 
int main(void)
{
	print_dir_info("CWD", QDir::current());
	print_dir_info("HOME", QDir::home());
	print_dir_info("ROOT", QDir::root());
	print_dir_info("TEMP", QDir::temp());
	print_dir_info("NONE", QDir("/None"));

	QDir tmp = QDir::temp();
	if(tmp.mkpath("qt/training"))
	{
		QDir mydir(tmp.path()+"/qt/training");
		QFile myf(mydir.path()+"/test.txt");
		if(myf.exists())
		{
			myf.remove();
		}
		if(myf.open(QFile::WriteOnly | QFile::Truncate))
		{
			QTextStream mys(&myf);
			mys << "Blah\n";
			mys << "Bleh\n";
		}
		myf.close();
		if(myf.open(QFile::ReadOnly))
		{
			QTextStream mys(&myf);
			qDebug() << mys.readAll();
		}
	}

	return 0;
}
