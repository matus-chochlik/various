#ifndef FRI_FIB_CALC_HPP
#define FRI_FIB_CALC_HPP

#include <QtCore>
#include <QUrl>
#include <QNetworkAccessManager>

class HttpGetter
 : public QObject
{
private:
	Q_OBJECT

	QNetworkAccessManager* _manager;
	QUrl _get_url;
public:
	explicit HttpGetter(QObject* parent);
	HttpGetter& setUrl(const QUrl&);
public slots:
	void sendRequest(void);
	void replyReceived(QNetworkReply*);
signals:
	void finished(void);
};

#endif
