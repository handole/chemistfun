import 'package:flutter/material.dart';
import '../../api/api_service.dart';
import '../../models/user.dart';
import '../auth/login_screen.dart';

class TeacherHomeScreen extends StatefulWidget {
  final User user;
  const TeacherHomeScreen({super.key, required this.user});

  @override
  State<TeacherHomeScreen> createState() => _TeacherHomeScreenState();
}

class _TeacherHomeScreenState extends State<TeacherHomeScreen> {
  int _currentIndex = 0;
  List<dynamic> _classes = [];
  List<dynamic> _journals = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    final cls = await ApiService.getClasses();
    final jrn = await ApiService.getJournals();
    if (mounted) {
      setState(() {
        _classes = cls;
        _journals = jrn;
        _loading = false;
      });
    }
  }

  void _logout() async {
    await ApiService.clearSession();
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  void _showCreateClassDialog() {
    final nameCtrl = TextEditingController();
    String grade = 'X';
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Buat Kelas Baru'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Nama Kelas (mis: X-MIPA 1)'),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: grade,
              items: const [
                DropdownMenuItem(value: 'X', child: Text('Kelas X')),
                DropdownMenuItem(value: 'XI', child: Text('Kelas XI')),
                DropdownMenuItem(value: 'XII', child: Text('Kelas XII')),
              ],
              onChanged: (v) => grade = v ?? 'X',
              decoration: const InputDecoration(labelText: 'Tingkat'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Batal')),
          ElevatedButton(
            onPressed: () async {
              if (nameCtrl.text.isNotEmpty) {
                await ApiService.createClass(nameCtrl.text.trim(), grade);
                Navigator.pop(ctx);
                _loadData();
              }
            },
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      appBar: AppBar(
        title: Text('Portal Guru - ${widget.user.fullName}'),
        backgroundColor: Colors.white,
        foregroundColor: const Color(0xFF1E293B),
        elevation: 0.5,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _currentIndex == 0
              ? _buildClassesTab()
              : _buildJournalsTab(),
      floatingActionButton: _currentIndex == 0
          ? FloatingActionButton.extended(
              onPressed: _showCreateClassDialog,
              icon: const Icon(Icons.add),
              label: const Text('Kelas Baru'),
            )
          : null,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.class_outlined),
            selectedIcon: Icon(Icons.class_),
            label: 'Manajemen Kelas',
          ),
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book),
            label: 'Jurnal Mengajar',
          ),
        ],
      ),
    );
  }

  Widget _buildClassesTab() {
    if (_classes.isEmpty) {
      return const Center(child: Text('Belum ada kelas yang dibuat'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _classes.length,
      itemBuilder: (ctx, i) {
        final c = _classes[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ListTile(
            contentPadding: const EdgeInsets.all(16),
            leading: CircleAvatar(
              backgroundColor: Colors.blue.shade100,
              child: Text(c['grade_level'] ?? 'X', style: const TextStyle(fontWeight: FontWeight.bold)),
            ),
            title: Text(c['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text('Kode Kelas: ${c['class_code']}'),
                Text('Siswa: ${c['student_count'] ?? 0} orang'),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildJournalsTab() {
    if (_journals.isEmpty) {
      return const Center(child: Text('Belum ada riwayat sesi jurnal'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _journals.length,
      itemBuilder: (ctx, i) {
        final j = _journals[i];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        j['title'] ?? '',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ),
                    Text(
                      j['date'] ?? '',
                      style: const TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text('Kelas: ${j['class_name'] ?? '-'}'),
                const SizedBox(height: 4),
                Text(
                  'Kehadiran: ${j['present_students'] ?? 0}/${j['total_students'] ?? 0} Siswa',
                  style: const TextStyle(fontSize: 13, color: Colors.blueGrey),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
