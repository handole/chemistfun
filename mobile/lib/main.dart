import 'package:flutter/material.dart';
import 'api/api_service.dart';
import 'models/user.dart';
import 'screens/auth/login_screen.dart';
import 'screens/student/student_home_screen.dart';
import 'screens/teacher/teacher_home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const KimiFunApp());
}

class KimiFunApp extends StatelessWidget {
  const KimiFunApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'KimiFun Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blueAccent,
          background: const Color(0xFFF6F8FC),
        ),
        fontFamily: 'Roboto',
      ),
      home: const SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final token = await ApiService.getToken();
    final user = await ApiService.getCurrentUser();

    if (!mounted) return;

    if (token != null && user != null) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => user.isTeacher
              ? TeacherHomeScreen(user: user)
              : StudentHomeScreen(user: user),
        ),
      );
    } else {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFFF6F8FC),
      body: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}
