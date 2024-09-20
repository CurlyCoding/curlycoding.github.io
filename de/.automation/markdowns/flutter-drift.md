# Flutter Drift
20. September 2024
![[flutter-drift.png]]
Die Speicherung lokaler Daten ist von grundlegender Bedeutung für jede App. Um komplexe Daten zu speichern, werden relationelle Datenbanken wie SQL benutzt. Wie auch viele andere Pakete implementiert Drift SQLite in Flutter. Im folgenden Artikel wirst du lernen, wie man eine Datenbank mit Drift erstellt und an dieser einfache Operationen ausführt.

## Warum Drift
Es gibt viele SQLite basierte Pakete für Dart, doch wieso sollte man sich für Drift entscheiden statt zum Beispeil für SQFlite? 

Drift ist besser als andere Pakete in den folgenden Punkten:
- Wenig unnötigen Code durch automatische Codegenerierung
- Nur Dart benötigt, keine SQL-Strings
- Alle Funktionalitäten von SQLite
- Verfügbar für alle Plattformen

## Installation
Füge die folgenden Pakete zur `pubspec.yaml` Datei hinzu:
```yaml
dependencies:
  drift: ^2.11.0
  sqlite3_flutter_libs: ^0.5.15
  path_provider: ^2.1.0
  path: ^1.8.3

dev_dependencies:
  drift_dev: ^2.11.0
  build_runner: ^2.4.6
```
Du kannst die aktuellen Versionen hier finden:
- [Drift](https://pub.dev/packages/drift/install)
- [sqlite3_flutter_libs](https://pub.dev/packages/sqlite3_flutter_libs/install)
- [path_provider](https://pub.dev/packages/path_provider/install)
- [path](https://pub.dev/packages/path/install)
- [drift_dev](https://pub.dev/packages/drift_dev/install)
- [build_runner](https://pub.dev/packages/build_runner/install)

## Beispiel
Die Funktionsweise von Dart soll an folgender relationeller Datenbank demonstriert werden: 

Eine Bücherei möchte die Ausleihen speichern. Dazu werden jeweils Tabellen für die Autoren, Bücher und Ausleihen erstellt.

## 1. Tabellen erstellen
Um eine Tabelle zu erstellen, erstellt man eine Klasse, die die Klasse `Table` erweitert. In einer Tabelle können nur bestimmte Dart Typen gespeichert werden. Die wichtigsten sind die folgenden:

| Dart Typ | Zeilentyp      | Zeile      |
| -------- | -------------- | ---------- |
| int      | IntColumn      | integer()  |
| double   | RealColumn     | real()     |
| boolean  | BooleanColumn  | boolean()  |
| String   | TextColumn     | text()     |
| DateTime | DateTimeColumn | dateTime() |

Die vollständige Liste kannst du [hier](https://drift.simonbinder.eu/docs/getting-started/advanced_dart_tables/) finden. Andere Datentypen können auch gespeichert werden, indem sie in eine dieser konvertiert werden. Siehe unten.

Du kannst eine Zeile mit dem Datentyp `int` und dem Namen `name` hinzufügen, indem du `IntColumn get name => integer()();` zur Tabellenklasse hinzufügts. 

Beispielsweise kann man so eine Tabelle mit Autoren erstellen, indem man eine nehe Datei `tables.dart` erstellt:

```dart
import 'package:drift/drift.dart';

class Authors extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get firstname => text()();
  TextColumn get lastname => text()();
  DateTimeColumn get birthday => dateTime()();
}
```

Es wird automatisch eine Id für einen Autor erstellt. Diese dient als Primärschlüssel. Alternativ kann auch selbst ein Primärschlüssel gebildet werden.

Bei Erstellung einer Zeile kann, diese bearbeitet werden, so dass sie zum Beispiel null beinhalten kann oder keinen Wert zwei mal enthalten kann. Dazu führt man eine Methode aus. Also zum Beispiel `integer().nullable()()` oder `text().unique()()`. Um mehrere Methoden zu nutzen, schreibt man diese einfach hintereinander.

```dart
class Books extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get title => text()();
  IntColumn get autorId => integer().references(Authors, #id)();
  TextColumn get genre => text().nullable()();
}
```

Mit `references` wird eine Spalte aus einer anderen Tabelle referenziert.

Erstellt man eine Tabelle, so wird automatisch einen Klasse für die Einträge erstellt. Dazu wird ein s am Ende des Tabellennamen entfernt, wenn es eins gibt. Um den Namen selbst zu bestimmen, benutzt man den Dekorator `@DataClassName`.

```dart
@DataClassName('LoanEntry')
class LoanEntries extends Table {
  IntColumn get id => integer().autoIncrement()();
  IntColumn get bookId => integer().references(Books, #id)();
  DateTimeColumn get returnDate => dateTime()();
}
```

Nun hat man alle Tabellen in der Datei `tables.dart` erstellt. 

## 2. Datenbank erstellen
Erstelle eine neue Datei `database.dart`.
```dart
import 'dart:io'; 
import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path_provider/path_provider.dart'; 
import 'tables.dart';
import 'package:path/path.dart' as p; 

part 'database.g.dart';

@DriftDatabase(tables: [Authors, Books, LoanEntries]) 
class MyDatabase extends _$MyDatabase { 
  MyDatabase() : super(_openConnection());

  @override int get schemaVersion => 1;
}
  
LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory(); 
    final file = File(p.join(dbFolder.path, 'db.sqlite')); 
    return NativeDatabase.createInBackground(file); 
  }); 
}
```
Führe `dart run build_runner build` aus. Durch diesen Befehl wird automatisch die Datei `database.g.dart` erstellt. Wundere dich also nicht, wieso zuerst bei `part 'database.g.dart';` eine Fehlermeldung auftaucht.

Die Datenbank mit den entsprechenden Tabellen wurde nun erstellt. Als nächstes werden für diese grundlegende Operationen implementiert: Die CRUD Operationen.

## 3. CRUD Operationen
Um die CRUD Operationen implementieren zu können, muss man erst wissen, was in der automatisch generierten Datei `database.g.dart` für Klassen erstellt wurden.

Die wichtigsten Klassen sind die Datenklasse und die Companion Klasse für jede Tabelle. Objekte der Datenklasse werden zurückgegeben, wenn Einträge aus einer Tabelle ausgelesen werden. Die Companion Klasse wird genutzt, um Einträge zu einer Tabelle hinzuzufügen oder sie zu aktualisieren. In der Companion Klasse muss um jedes Attribut mit `Value()` umhüllt werden. Also `Value('book')` statt `'book'`.  In der Companion Klasse kann man Zeilen, die nullable sind oder einen Default Wert von `.default()` haben, ggf. nicht angeben und stattdessen `Value.absent()` einsetzen.

### Hinzufügen
```dart
Future<void> addLoanEntry({
  required int bookId,
  required DateTime returnDate,
}) async {
  into(loanEntries).insert(LoanEntriesCompanion.insert(
    bookId: bookId,
    returnDate: returnDate,
  ));
}
```
Es wird zur Tabelle `loanEntries` ein Eintrag hinzugefügt.

### Auslesen
```dart
Future<Book> getBookById(int id) async {
  return await (select(books)..where((t) => t.id.equals(id))).getSingle();
}

Stream<List<LoanEntry>> getLoanEntries() {
  return select(loanEntries)).watch();
}
```
Daten können als Future oder als Stream zurückgegeben werden. Dazu wird `.get()` und `.watch()` benutzt. Wenn man weiß, dass beim Auslesen nur ein Eintrag zurückgegeben wird, können die Methoden `.getSingle()` und `.watchSingle()` verwendet werden.

### Aktualisieren
```dart
Future<void> updateLoanEntry(LoanEntriesCompanion entry) async {
  (update(loanEntries)..where((t) => t.id.equals(entry.id.value))).write(entry);
}

// Beispiel:
// updateLoanEntry(LoanEntriesCompanion(
//   bookId: Value.absent(),
//   returnDate: Value(DateTime(2023, 9, 7)),
// ));
```
Bei Werten, die nicht aktualisiert werden sollen, wird nur `Value.absent` angegeben.

### Löschen
```dart
Future<void> deleteLoanEntry(int id) async {
  (delete(loanEntries)..where((t) => t.id.equals(id))).go();
}
```
Es wird nach der Eintrag mit der entsprechenden Id gelöscht. Wählt man mit `..where()` mehrere Einträge aus, werden alle gelöscht.

## 4. Konvertierung
Möchte man statt den herkömmlichen Datentypen seine eigenen speichern, müssen diese erst in einen speicherbaren Datentypen konvertiert werden.

Dazu erstellt man eine Klasse, die `TypeConverter<Type1, Type2>` erweitert. Statt `Type1` gibt man die eigene Klasse an und für `Type2` die speicherbare Klasse. Für diese Klasse müssen nun zwei Methoden implementiert werden: `toSql` und `fromSql`.

Hat man zum Beispiel eine Klasse `Name`, von der eine Instanz in jedem Objekt der Klasse `Author` gespeichert werden soll, sieht dies so aus:

```dart
class Name {
  String firstname,
  String lastname,

  Name(this.firstname, this.lastname);
}

class NameConverter extends TypeConverter<Name, String> {
  @override
  String toSql(Name name) => name.firstname + ';' + name.lastname;

  @override
  Name fromSql(String str) {
    final nm = str.split(';');
    return Name(nm[0], nm[1]);
  }
}

class Authors extends Table {
    IntColumn get id => integer().autoIncrement()();
  TextColumn get name => text().map(const NameConverter())();
  DateTimeColumn get birthday => dateTime()();
}
```

Die automatisch generierte Klasse `Author` hat in diesem Fall ein Attribut `name` mit dem Typ `Name`.

## Fazit
Insgesamt hast du also gelernt, wie man mit Drift eine SQLite Datenbank erstellt und auf dieser grundlegende Operationen ausführt. Es gibt noch viele weitere Features in Drift wie zum Beispiel JOINS. Mehr Informationen kannst du in offiziellen [Drift Dokumentation](https://drift.simonbinder.eu/) finden.