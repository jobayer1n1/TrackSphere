import 'package:flutter/material.dart';

import 'home.dart';
import 'login.dart';

void main() {
  runApp(const TrackSphereApp());
}

class TrackSphereApp extends StatelessWidget {
  const TrackSphereApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TrackSphere',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const LoginPage(),
      onGenerateRoute: (settings) {
        if (settings.name == '/home') {
          final accessToken = settings.arguments as String?;
          if (accessToken != null && accessToken.isNotEmpty) {
            return MaterialPageRoute(
              builder: (_) => HomePage(accessToken: accessToken),
            );
          }
        }
        return null;
      },
    );
  }
}
