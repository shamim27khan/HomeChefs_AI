import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'config/theme.dart';
import 'providers/auth_provider.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/register_screen.dart';
import 'screens/splash_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final authProvider = AuthProvider(prefs);
  await authProvider.initialize();

  runApp(
    ChangeNotifierProvider.value(
      value: authProvider,
      child: const HomeChefsApp(),
    ),
  );
}

class HomeChefsApp extends StatelessWidget {
  const HomeChefsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HomeChefHub',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/home': (context) => const HomeScreen(),
      },
    );
  }
}