TEMPLATE   = app
QT        += core quick

TARGET     = primes

SOURCES   += main.cpp finder.cpp
HEADERS   += finder.hpp
RESOURCES += main.qrc

lupdate_only {
SOURCES    = primes.qml
}

TRANSLATIONS += primes_sk.ts
