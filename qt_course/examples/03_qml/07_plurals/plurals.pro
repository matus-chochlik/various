TEMPLATE   = app
QT        += core quick

TARGET     = plurals

SOURCES   += main.cpp
RESOURCES += main.qrc

lupdate_only {
SOURCES    = plurals.qml
}

TRANSLATIONS += plurals_sk.ts
