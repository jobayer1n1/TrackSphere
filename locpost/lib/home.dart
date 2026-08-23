import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'login.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.accessToken});

  final String accessToken;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _vehicleIdController = TextEditingController();
  final TextEditingController _endpointController = TextEditingController();

  Timer? _locationTimer;
  bool _isTracking = false;
  bool _isSending = false;
  Position? _lastPosition;
  String _status = 'Not tracking';

  @override
  void dispose() {
    _locationTimer?.cancel();
    _vehicleIdController.dispose();
    _endpointController.dispose();
    super.dispose();
  }

  Future<bool> _checkLocationPermission() async {
    final serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      setState(() => _status = 'Location service is disabled');
      return false;
    }

    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        setState(() => _status = 'Location permission denied');
        return false;
      }
    }

    if (permission == LocationPermission.deniedForever) {
      setState(() => _status = 'Location permission permanently denied');
      await Geolocator.openAppSettings();
      return false;
    }

    return true;
  }

  Future<void> _sendLocation() async {
    if (_isSending) return;

    setState(() {
      _isSending = true;
      _status = 'Getting location...';
    });

    try {
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
      );
      _lastPosition = position;

      final response = await http.post(
        Uri.parse(_endpointController.text.trim()),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${widget.accessToken}',
        },
        body: jsonEncode({
          'vehicle_id': int.parse(_vehicleIdController.text.trim()),
          'latitude': position.latitude,
          'longitude': position.longitude,
          'timestamp': DateTime.now().toUtc().toIso8601String(),
        }),
      );

      setState(() {
        _status = response.statusCode >= 200 && response.statusCode < 300
            ? 'Location sent successfully'
            : 'Server error: ${response.statusCode}';
      });
    } catch (e) {
      setState(() => _status = 'Failed: $e');
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  Future<void> _startTracking() async {
    final vehicleId = _vehicleIdController.text.trim();
    final endpoint = _endpointController.text.trim();

    if (int.tryParse(vehicleId) == null) {
      _showError('Vehicle ID must be a numeric backend vehicle ID.');
      return;
    }
    if (endpoint.isEmpty) {
      _showError('Please enter the location update endpoint.');
      return;
    }

    final uri = Uri.tryParse(endpoint);
    if (uri == null || !uri.hasScheme || uri.host.isEmpty) {
      _showError('Please enter a valid endpoint URL.');
      return;
    }
    if (!await _checkLocationPermission()) return;

    setState(() {
      _isTracking = true;
      _status = 'Tracking started';
    });

    await _sendLocation();
    _locationTimer = Timer.periodic(
      const Duration(seconds: 2),
      (_) => _sendLocation(),
    );
  }

  void _stopTracking() {
    _locationTimer?.cancel();
    _locationTimer = null;
    setState(() {
      _isTracking = false;
      _status = 'Tracking stopped';
    });
  }

  Future<void> _logout() async {
    _locationTimer?.cancel();
    _locationTimer = null;

    final preferences = await SharedPreferences.getInstance();
    await preferences.remove(sessionTokenKey);

    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginPage()),
      (route) => false,
    );
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vehicle Tracking'),
        actions: [
          IconButton(
            onPressed: _logout,
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Log out',
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Icon(Icons.location_on_rounded, size: 64, color: theme.colorScheme.primary),
            const SizedBox(height: 12),
            Text(
              'Vehicle Location',
              style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Configure the vehicle and location update endpoint to start sending GPS data.',
              style: theme.textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _vehicleIdController,
              enabled: !_isTracking,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'Vehicle ID',
                hintText: 'e.g. 1',
                prefixIcon: Icon(Icons.directions_car_rounded),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _endpointController,
              enabled: !_isTracking,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: 'Location Update Endpoint',
                hintText: 'http://192.168.1.100:8000/api/locations',
                prefixIcon: Icon(Icons.cloud_upload_rounded),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          _isTracking ? Icons.radio_button_checked : Icons.radio_button_unchecked,
                          color: _isTracking ? theme.colorScheme.primary : theme.colorScheme.outline,
                        ),
                        const SizedBox(width: 12),
                        Expanded(child: Text(_status, style: theme.textTheme.bodyLarge)),
                      ],
                    ),
                    if (_lastPosition != null) ...[
                      const SizedBox(height: 16),
                      const Divider(),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          const Icon(Icons.my_location_rounded),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Lat: ${_lastPosition!.latitude.toStringAsFixed(6)}\n'
                              'Lng: ${_lastPosition!.longitude.toStringAsFixed(6)}',
                            ),
                          ),
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (!_isTracking)
              FilledButton.icon(
                onPressed: _startTracking,
                icon: const Icon(Icons.play_arrow_rounded),
                label: const Text('Start Tracking'),
              )
            else
              FilledButton.tonalIcon(
                onPressed: _stopTracking,
                icon: const Icon(Icons.stop_rounded),
                label: const Text('Stop Tracking'),
              ),
            const SizedBox(height: 12),
            if (_isSending)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(12),
                  child: CircularProgressIndicator(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}