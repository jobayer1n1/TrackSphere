import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:locpost/login.dart';

void main() {
  testWidgets('Login screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginPage()));

    expect(find.text('TrackSphere Login'), findsOneWidget);
    expect(find.text('Sign in to send vehicle location'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });
}
