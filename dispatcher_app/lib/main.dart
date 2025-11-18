import 'package:flutter/material.dart';
import 'dispatcher_home_screen.dart';

void main() {
  runApp(DispatcherApp());
}

class DispatcherApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dispatcher App',
      theme: ThemeData(
        primarySwatch: Colors.orange,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: DispatcherHomeScreen(),
    );
  }
}
