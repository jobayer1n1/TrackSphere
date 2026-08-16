import 'package:flutter_test/flutter_test.dart';

import 'package:locpost/main.dart';

void main() {
  testWidgets('Locpost starter screen renders', (WidgetTester tester) async {
    await tester.pumpWidget(const LocpostApp());

    expect(find.text('Locpost'), findsOneWidget);
    expect(find.text('Locpost is ready'), findsOneWidget);
  });
}
