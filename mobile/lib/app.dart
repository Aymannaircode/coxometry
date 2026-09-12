import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'services/radiograph_picker.dart';
import 'theme/app_theme.dart';

class CoxometrieApp extends StatelessWidget {
  const CoxometrieApp({
    super.key,
    this.picker,
  });

  final RadiographPicker? picker;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Coxométrie',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: HomeScreen(
        picker: picker ?? FileRadiographPicker(),
      ),
    );
  }
}
