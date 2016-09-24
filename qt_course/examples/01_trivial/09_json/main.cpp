#include <QJsonObject>
#include <QJsonDocument>
#include <QJsonParseError>
#include <QDebug>

int main(void)
{
	QString jsonText("{"
	" \"name\": \"Johnny\","
	" \"middlename\": \"B.\","
	" \"surname\": \"Goode\","
	" \"city\": \"New Orleans\""
	"}");

	QJsonParseError jsonErr;
	QJsonDocument jsonDoc = QJsonDocument::fromJson(
		jsonText.toUtf8(),
		&jsonErr
	);

	if(jsonErr.error != QJsonParseError::NoError) {
		qDebug() << jsonErr.errorString();
		return 1;
	}

	QJsonObject jsonObj = jsonDoc.object();

	qDebug() << "name:" << jsonObj["name"].toString();
	qDebug() << "surname:" << jsonObj["surname"].toString();
	qDebug() << "city:" << jsonObj["city"].toString();

	return 0;
}
