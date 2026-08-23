import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

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
      home: const SessionGate(),
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

class SessionGate extends StatefulWidget {
  const SessionGate({super.key});

  @override
  State<SessionGate> createState() => _SessionGateState();
}

class _SessionGateState extends State<SessionGate> {
  late final Future<String?> _sessionToken = _loadSessionToken();

  Future<String?> _loadSessionToken() async {
    final preferences = await SharedPreferences.getInstance();
    return preferences.getString(sessionTokenKey);
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String?>(
      future: _sessionToken,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        final accessToken = snapshot.data;
        if (accessToken == null || accessToken.isEmpty) {
          return const LoginPage();
        }
        return HomePage(accessToken: accessToken);
      },
    );
  }
}
