import 'package:flutter/material.dart';
import '../../api/api_service.dart';
import '../../models/user.dart';
import '../teacher/teacher_home_screen.dart';
import '../student/student_home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailCtrl = TextEditingController(text: 'kimisifu@mail.com');
  final _passCtrl = TextEditingController(text: 'H@555iv02#');
  final _nameCtrl = TextEditingController();
  final _inviteCtrl = TextEditingController();

  bool _isRegister = false;
  String _selectedRole = 'student';
  bool _loading = false;
  String? _errorMessage;

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _errorMessage = null;
    });

    try {
      if (_isRegister) {
        if (_nameCtrl.text.trim().isEmpty) {
          throw Exception('Nama lengkap wajib diisi');
        }
        if (_selectedRole == 'teacher' && _inviteCtrl.text.trim().isEmpty) {
          throw Exception('Kode undangan guru wajib diisi');
        }

        final res = await ApiService.register(
          email: _emailCtrl.text.trim(),
          password: _passCtrl.text,
          fullName: _nameCtrl.text.trim(),
          role: _selectedRole,
          teacherInviteCode: _inviteCtrl.text.trim(),
        );

        if (!res['ok']) throw Exception(res['message']);
        _navigateUser(res['user'] as User);
      } else {
        final res = await ApiService.login(
          _emailCtrl.text.trim(),
          _passCtrl.text,
        );
        if (!res['ok']) throw Exception(res['message']);
        _navigateUser(res['user'] as User);
      }
    } catch (e) {
      setState(() => _errorMessage = e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _navigateUser(User user) {
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => user.isTeacher
            ? TeacherHomeScreen(user: user)
            : StudentHomeScreen(user: user),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 400),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Logo & Header
                const Center(
                  child: Icon(Icons.science, size: 48, color: Colors.blueAccent),
                ),
                const SizedBox(height: 12),
                const Text(
                  'KimiFun Mobile',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _isRegister ? 'Buat akun pembelajaran baru' : 'Masuk ke portal pembelajaran kimia',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
                ),
                const SizedBox(height: 24),

                if (_errorMessage != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: TextStyle(color: Colors.red.shade700, fontSize: 13),
                    ),
                  ),

                if (_isRegister) ...[
                  TextField(
                    controller: _nameCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Nama Lengkap',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    value: _selectedRole,
                    decoration: const InputDecoration(
                      labelText: 'Role Akun',
                      border: OutlineInputBorder(),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'student', child: Text('👨‍🎓 Siswa (Student)')),
                      DropdownMenuItem(value: 'teacher', child: Text('👨‍🏫 Guru (Teacher)')),
                    ],
                    onChanged: (val) => setState(() => _selectedRole = val ?? 'student'),
                  ),
                  const SizedBox(height: 16),
                  if (_selectedRole == 'teacher') ...[
                    TextField(
                      controller: _inviteCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Kode Undangan Guru',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                ],

                TextField(
                  controller: _emailCtrl,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _passCtrl,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Password',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 24),

                ElevatedButton(
                  onPressed: _loading ? null : _submit,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    backgroundColor: Colors.blueAccent,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _loading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : Text(_isRegister ? 'Daftar Sekarang' : 'Masuk'),
                ),
                const SizedBox(height: 16),

                TextButton(
                  onPressed: () => setState(() {
                    _isRegister = !_isRegister;
                    _errorMessage = null;
                  }),
                  child: Text(
                    _isRegister
                        ? 'Sudah punya akun? Masuk'
                        : 'Belum punya akun? Daftar sebagai siswa',
                    style: const TextStyle(fontSize: 13),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
