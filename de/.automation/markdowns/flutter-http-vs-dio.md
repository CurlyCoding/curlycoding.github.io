# Flutter http vs Dio
20. September 2024
![[flutter-http-vs-dio.png]]
Sowohl Dio als auch http bieten die Möglichkeit Netzwerkanfragen in Flutter durchzuführern. Im folgenden werden beide Pakete miteinander verglichen und es wird erläutert, wann welches Paket am besten geeignet ist.

## Was ist http?
[http](https://pub.dev/packages/http) ist ein Paket von dem offiziellen Dart Team, um essentielle Funktionen zum Netzwerken in Dart bereitzustellen.

**Vorteile**
- **Vom offiziellen Dart Team**: Da http vom offiziellen Dart Team entwickelt wurde, kann damit gerechnet werden, dass http in Zukunft weiterhin unterstützt wird und bugs schneller behoben werden
- **Größe**: Da sich http nur auf die essentiellsten Features beschränkt, ist das Paket dementsprechend relativ klein
- **Einfache Verwendung**: http ist einfach zu erlernen und zu verwenden

**Nachteile**
- **Begrenzte Funktionalität**: http bietet nur die wichtigsten Funktionen für Netzwerkanfragen an
## Was ist Dio?
[Dio](https://pub.dev/packages/dio) stellt viele nützliche Funktionen zu Verfügung, damit nicht immer wieder für die gleiche Anwendung neue Funktionen implementiert werden müssen.

**Vorteile**
- **Umfassende Funktionalität**: Dio bietet viele Features für die meisten Fälle, in denen man Netzwerkanfragen braucht, wie zum Beispiel Interceptors, FormData oder Anfragestornierung
- **Einfache Verwendung**: Dio ist einfach zu erlernen und zu verwenden

**Nachteile**
- **Größe**: Da Dio so viel Funktionalität beinhaltet, führt dies zu einen größeren App-Download
- **Geringe Zuverlässigkeit**: Es gibt viele Bugs und Dio wird nicht mehr gepflegt

## Fazit
Für kleinere Projekte kann mit Dio leicht Zeit gespart werden, da es viel mehr Features gibt, die nicht extra implementiert werden müssen. Für größere Projekte sollte man besser http verwenden und seine eigene Funktionen für komplexere Anwendungen schreiben. So wird garantiert, dass nicht mit der Zeit irgendwelche Bugs in Dio auftauchen, die das Projekt belasten.