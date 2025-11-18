import 'package:flutter/material.dart';
import 'receiver_home_screen.dart';

void main() {
  runApp(ReceiverApp());
}

class ReceiverApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Receiver App',
      theme: ThemeData(
        primarySwatch: Colors.green,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: ReceiverHomeScreen(),
    );
  }
}
