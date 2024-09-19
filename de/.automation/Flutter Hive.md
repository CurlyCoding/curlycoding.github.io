![[img_hive.png]]

Hive ist eine schnelle und einfache Möglichkeit, um Key-Value Paare lokal zu speichern. Hive ist effizienter als die übliche Methode `shared_preferences` und bietet mehr Features, wie zum Beispiel die Speicherung eigener Datentypen oder die Verschlüsselung von Daten.

In Hive werden die Daten in sogenannten Boxen gespeichert. Eine Box kann viele verschiedene Datentypen speichern. 

## Hive einrichten
Um Hive zu nutzen, musst du folgende Pakete zur `pubspex.yaml` Datei hinzufügen:

```yaml
dependencies:
  hive: ^2.2.3
  hive_flutter: ^1.1.0

dev_dependencies:
  hive_generator: ^2.0.1
  build_runner: ^2.4.6
```

Die neusten Versionen kannst du hier finden:
- [hive](https://pub.dev/packages/hive)
- [hive_flutter](https://pub.dev/packages/hive_flutter)
- [hive_generator](https://pub.dev/packages/hive_generator)
- [build_runner](https://pub.dev/packages/build_runner)

Zuerst muss Hive initialisiert werden. Dafür die `main` Funktion wie folgt verändern:
```dart
import 'package:hive/hive.dart';

void main() async {
  await Hive.initFlutter();

  runApp(myApp());
}
```

Um nun Daten zu speichern und auszulesen, muss man eine Box öffnen.
```dart
var box = await Hive.openBox();
```

Beim Öffnen einer Box, kann der Name der Box spezifiziert werden. Für jeden Namen wird einen andere Box geöffnet, wird kein Name angegeben, eine bestimmte Standardbox.
```dart
var box = await Hive.openBox('name');
```

Nachdem eine Box geöffnet wurde, kann diese einfach mit `Hive.box('name')` wird genutzt werden. Dabei muss hier nicht `await` genutzt werden, da dieser Befehl synchron ausgeführt wird. Beispielsweise kann man direkt man der Initialisierung von Hive in der `main` Funktion eine Box öffnen und sie dann später einfach nutzen ohne asynchronen Code schreiben zu müssen.

Sobald man die Box nicht mehr öffnen muss, kann diese mit `box.close();` geschlossen werden. Dies muss allerdings nicht gemacht werden, da sich die Box allein schließt, wenn sie nicht mehr gebraucht wird.

Normalerweise können in einer Box viele verschiedene Daten mit unterschiedlichen Datentypen gespeichert werden. Um in einer Box nur einen Datentypen z.B. Strings speichern zu können, benutzt man folgenden Befehl:
```dart
var box = await Hive.openBox<String>('myBox');
```
Wenn die gleiche Box nun erneut geöffnet wird, muss darauf geachtet werden, dass nur dieser Datentyp gespeichert wird und wieder die gleiche Notation beim Öffnen verwendet wird.

## Daten speichern, auslesen und löschen
Um Daten in einer Box zu speichern, weißt man einem Textschlüssel ein Objekt zu. Es können primitive Darttypen, Listen und Directories gespeichert werden. Außerdem kann man mit einem TypeAdapter eigene Datentypen speichern.

Dies sieht beispielsweise so aus:
```dart
box.put("key", 0);
box.putAll({"k1": "val", "k2": 2});

var val = box.get("key");
var values = box.values;

box.delete("key");
box.clear();
```
Um einen Eintrag hinzuzufügen, wird `put` benutzt, für mehrere Einträge nutzt man `putAll`. 

Mit `get` wird der Wert zurückgegeben, der dem Schlüssel zugeordnet ist. Wenn dem Schlüssel kein Wert zugeordnet ist, wird `null` zurückgegeben. Mit `box.values` erhält man alle Werte in der Box.

Mit `del` wird ein Eintrag gelöscht. Mit `clear` werden alle Einträge gelöscht und.

## Eigene Datentypen: TypeAdapter
Um eigene Datentypen in einer Box zu speichern, muss zuerst die entsprechende Klasse erstellt werden.
```dart
import 'package:hive/hive.dart';

part ‘person.g.dart’;

@HiveType(typeId: 0)
class Person {
  Person({required this.name, required this.age});

  @HiveField(0)
  String name;

  @HiveField(1)
  int age;
}
```

Jedem Attribut der Klasse wird ein HiveField zugewiesen und der Klasse ein HiveType. Hier ist der Code beinhaltet in der Datei `person.dart`. Je nachdem wie die Datei heißt, sollte man die Zeile mit `part ‘person.g.dart’;` anpassen. Die Datei `person.g.dart` wird automatisch generiert, sobald man im Terminal `flutter packages pub run build_runner build` ausführt. Diese Datei beinhaltet einen TypeAdapter, den man zuerst in Hive registrieren muss, bevor die Daten der eigene Klasse gespeichert werden können.
```dart
Hive.registerAdapter(PersonAdapter());
```
Dies sollte man direkt nach der Initialisierung von Hive machen. Also:
```dart
import 'package:hive_flutter/hive_flutter.dart';

void main() async {
  await Hive.initFlutter();
  Hive.registerAdapter(PersonAdapter());

  runApp(myApp());
}
```

## Große Datenmengen: Lazy box
Bei Benutzung der üblichen Box von Hive wird der gesamte Inhalt der Box im Arbeitsspeicher gespeichert, sobald die Box geöffnet wird. Für kleinere Datenmengen ist dies unproblematisch und praktisch, da so die Daten später synchron aufgerufen werden können. 

Für größere Datenmengen belastet dies allerdings zunehmend den Arbeitsspeicher. Deswegen sollte man in diesen Fälle die lazy box benutzen. Diese lädt beim Öffnen alle Schlüssel und die Orte der Werte. Bei Bedarf werden die Werte dann aufgerufen.

```dart
var lazyBox = await Hive.openLazyBox('myLazyBox'); 

var value = await lazyBox.get('lazyVal');
```
Hier müssen Datenaufrufe mit `await` gekennzeichnet werden. Ist eine lazy box bereits geöffnet, kann diese synchron mit `Hive.lazyBox('myLazyBox')`  zurückgegeben werden.

## Vertrauliche Daten: Verschlüsselte box
Möchte man vertrauliche Daten in einer Box speichern, sollte eine verschlüsselte Box verwenden. Diese Box verschlüsselt alle Werte, die einem Schlüssel zugewiesen wurden mit der AES-256 Verschlüsselung. Die Schlüssel werden nicht verschlüsselt. Der Verschlüsselungsschlüssel muss auch sicher gespeichert werden, wie zum Beispiel mit dem Paket [flutter_secure_storage](https://pub.dev/packages/flutter_secure_storage).

```dart
import 'dart:convert';
import 'package:hive/hive.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const secureStorage = FlutterSecureStorage();
final encryptionKeyString = await secureStorage.read(key: 'key');
if (encryptionKeyString == null) {
  final key = Hive.generateSecureKey();
  await secureStorage.write(
    key: 'key',
    value: base64UrlEncode(key),
  );
}
final key = await secureStorage.read(key: 'key');
final encryptionKey = base64Url.decode(key!);

final encryptedBox = await Hive.openBox('vaultBox', encryptionCipher: HiveAesCipher(encryptionKey));
var value = encryptedBox.put('secret');
```
Hier wird mit flutter_secure_storage ein Schlüssel gespeichert. Wenn es noch keinen gibt, wird automatisch ein sicherer Schlüssel von Hive erzeugt und dieser wird mit flutter_secure_storage in der Base64 Kodierung gespeichert. Dann wird der Schlüssel ausgelesen, der nun auf jeden Fall existiert, von Base64 dekodiert und aus Entschlüsselungsschlüssel der Box angegeben.
## Fazit
Wie man sieht, bietet Hive eine einfache und effiziente Möglichkeit Daten zu speichern. Hive hat viele wichtige Features wie synchrone, asynchrone Boxen und verschlüsselte Boxen. Hive eignet sich sowohl für kleine Datenmengen als auch für größere Datenmengen. Mehr Informationen kannst du in der [Hive Dokumentation](https://docs.hivedb.dev/) finden.