import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'home.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController _serverController = TextEditingController(
    text: 'http://10.0.2.2:8000',
  );
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;

  @override
  void dispose() {
    _serverController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    final serverUrl = _serverController.text.trim().replaceFirst(RegExp(r'/$'), '');
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (serverUrl.isEmpty || email.isEmpty || password.isEmpty) {
      _showError('Enter the server URL, email, and password.');
      return;
    }

    final serverUri = Uri.tryParse(serverUrl);
    if (serverUri == null || !serverUri.hasScheme || serverUri.host.isEmpty) {
      _showError('Enter a valid server URL.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('$serverUrl/api/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode < 200 || response.statusCode >= 300) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(data['detail'] ?? 'Login failed');
      }

      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final accessToken = data['access_token'] as String?;
      if (accessToken == null || accessToken.isEmpty) {
        throw Exception('Login response did not contain an access token.');
      }

      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomePage(accessToken: accessToken),
        ),
      );
    } catch (e) {
      _showError(e.toString().replaceFirst('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('TrackSphere Login')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            const Icon(Icons.lock_outline_rounded, size: 64),
            const SizedBox(height: 16),
            Text(
              'Sign in to send vehicle location',
              style: Theme.of(context).textTheme.headlineSmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            TextField(
              controller: _serverController,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: 'Backend server URL',
                hintText: 'http://10.0.2.2:8000',
                prefixIcon: Icon(Icons.dns_outlined),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: 'Email',
                prefixIcon: Icon(Icons.email_outlined),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              onSubmitted: (_) => _login(),
              decoration: const InputDecoration(
                labelText: 'Password',
                prefixIcon: Icon(Icons.password_outlined),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: _isLoading ? null : _login,
              icon: _isLoading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.login_rounded),
              label: Text(_isLoading ? 'Signing in...' : 'Sign in'),
            ),
          ],
        ),
      ),
    );
  }
}