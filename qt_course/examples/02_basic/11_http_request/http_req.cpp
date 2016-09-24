#include "http_req.hpp"
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>

HttpGetter::HttpGetter(QObject* parent)
 : QObject(parent)
 , _manager(new QNetworkAccessManager(this))
{
	connect(
		_manager, SIGNAL(finished(QNetworkReply*)),
		this,  SLOT(replyReceived(QNetworkReply*))
	);
}

HttpGetter& HttpGetter::setUrl(const QUrl& url)
{
	_get_url = url;
	return *this;
}

void HttpGetter::sendRequest(void)
{
	_manager->get(QNetworkRequest(_get_url));
}

void HttpGetter::replyReceived(QNetworkReply* reply)
{
	if(reply->error())
	{
		qDebug() << "Error";
		qDebug() << reply->errorString();
	}
	else
	{
		qDebug() << reply->header(QNetworkRequest::ContentTypeHeader).toString();
		qDebug() << reply->readAll();
	}
	emit finished();
}

#include "moc_http_req.cpp"

