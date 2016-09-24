#include <QCoreApplication>
#include "http_req.hpp"

int main(int argc, char *argv[])
{
	QCoreApplication app(argc, argv);

	HttpGetter* hget = new HttpGetter(&app);

	QObject::connect(hget, SIGNAL(finished()), &app, SLOT(quit()));

	QUrl url("http://jsonplaceholder.typicode.com/users/1");
	hget->setUrl(url);
	QTimer::singleShot(0, hget, SLOT(sendRequest()));

	return app.exec();
}
