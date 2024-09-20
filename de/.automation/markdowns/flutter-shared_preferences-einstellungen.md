# Flutter shared preferences: Einstellungen speichern
20. September 2024
![[flutter-shared-preferences.png]]
SharedPreferences ist ein Flutter-Paket, mit der du einfach Daten speichern kannst. Dazu weist man einen Schlüssel eine Zahl, Zeichenkette oder Wahrheitswert zu und kann diesen immer leicht wieder aufrufen. SharedPreferences kann für alle Plattformen benutzt werden.

## 1. Installation
Füge zu `pubspec.yaml` folgendes hinzu:
```
dependecies:
 shared_preferences: ^2.2.0
```
Du kannst die neuste Version [hier](https://pub.dev/packages/shared_preferences/install) finden.

Um SharedPreferences nun in einer Datei zu nutzen, musst du einfach das Paket importieren mit:
```dart
import 'package:shared_preferences/shared_preferences.dart';
```
Dann erstellst du eine Instanz von SharedPreferences mit
```dart
SharedPreferences prefs = await SharedPreferences.getInstance();
```

## 2. SharedPreferences Methoden
Die folgenden Dart Datentypen können mit SharedPreferences gespeichert werden:
- `int`
- `double`
- `String`
- `bool`

Andere Daten können auch gespeichert werden, indem diese erst in eine dieser Datentypen konvertiert wird und beim Auslesen wieder in die ursprüngliche Form bringen.

### Hinzufügen
```dart
prefs.setInt('int_key', 1);
prefs.setDouble('double_key', 3.14)
prefs.setString('string_key', 'value');
prefs.setBool('bool_key', true);
```
Jedem Schlüssel kann höchstens ein Datentyp zugewiesen werden. Wird dem Schlüssel ein neuer Wert zugewiesen, wird der letzte gelöscht.

### Auslesen
```dart
int v1 = prefs.getInt('int_key');
double v2 = prefs.getDouble('double_key');
String v3 = prefs.getString('string_key');
bool v4 = prefs.getBool('bool_key');
```
Wird ein get-Methode eines Datentypen für einen Schlüssel aufgerufen, bei dem nicht diese Datentyp gespeichert wurde, wird `null` zurückgegeben.

### Löschen
Daten, die einem bestimmten Schlüssel zugeordnet, können gelöscht werden mit der `prefs.remove` Methode:
```dart
prefs.remove('key');
```

### Prüfen, ob Daten gespeichert sind
Es kann einfach überprüft werden, ob einem Schlüssel ein Wert zugeordnet sind:
```dart
prefs.containsKey('key');
```
Die Methode gibt einen Wahrheitswert zurück - `true`, wenn Wert vorhanden, sonst `false`.

## 3. Standardwerte
Beispielsweise bei der Implementation von Voreinstellungen ist es nützlich einen bestimmten Schlüssel einen Standardwert zugeben. Da standardmäßig jedem Schlüssel `null` zugewiesen ist, kann man mit dem `??` Operator arbeiten:
```dart
bool v = prefs.getBool('dark') ?? false;
```

Falls der Wert vor dem `??` Operator `null` ist, wird der Wert nach dem `??` zurückgegeben, sonst der normale Wert.

## 4. Beispiel: Light und Dark Mode Counter App
Nun soll die Verwendung von SharedPreferences an der Standard Counter App demonstriert werden. Es soll sowohl ein Dark Mode implementiert werden, also auch der Zähler gespeichert werden.

Dazu erstellt man drei Methoden: Eine zum Speichern der Dark Mode Einstellung, zum Speichern des Zählers und zum Laden der Daten.
```dart
void _toggleDark(bool value) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  setState(() {
    _dark = value;
    prefs.setBool('dark', value);
  });
}

void _incrementCounter() async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  setState(() {
    _counter++;
    prefs.setInt('counter', _counter);
  });
}

void _loadData() async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  setState(() {
    _counter = (prefs.getInt('counter') ?? 0);
    _dark = (prefs.getBool('dark') ?? true);
  });
}
```

![[shared-pre-scr1.png]]
![[shared-pre-scr2.png]]

Im folgenden siehst du den gesamten Code der `main.dart` Datei:
```dart
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  int _counter = 0;
  bool _dark = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _toggleDark(bool value) async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _dark = value;
      prefs.setBool('dark', value);
    });
  }

  void _incrementCounter() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _counter++;
      prefs.setInt('counter', _counter);
    });
  }

  void _loadData() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    setState(() {
      _counter = (prefs.getInt('counter') ?? 0);
      _dark = (prefs.getBool('dark') ?? true);
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: _dark ? Brightness.dark : Brightness.light,
        useMaterial3: true,
      ),
      home: Scaffold(
        appBar: AppBar(
          backgroundColor: Theme.of(context).colorScheme.inversePrimary,
          title: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                "Dark mode",
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              Switch(
                value: _dark,
                onChanged: (value) => _toggleDark(value),
              ),
            ],
          ),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              const Text(
                'You have pushed the button this many times:',
              ),
              Text(
                '$_counter',
                style: const TextStyle(fontSize: 33),
              ),
            ],
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: _incrementCounter,
          child: const Icon(Icons.add),
        ),
      ),
    );
  }
}
```