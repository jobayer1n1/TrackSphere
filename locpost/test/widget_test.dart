import 'package:flutter_test/flutter_test.dart';

import 'package:locpost/main.dart';

void main() {
  testWidgets('Login screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(const TrackSphereApp());

    expect(find.text('TrackSphere Login'), findsOneWidget);
    expect(find.text('Sign in to send vehicle location'), findsOneWidget);
    expect(find.text('Sign in'), findsOneWidget);
  });
}
