import 'package:flutter/material.dart';
import '../../api/api_service.dart';
import '../../models/user.dart';
import '../auth/login_screen.dart';

class StudentHomeScreen extends StatefulWidget {
  final User user;
  const StudentHomeScreen({super.key, required this.user});

  @override
  State<StudentHomeScreen> createState() => _StudentHomeScreenState();
}

class _StudentHomeScreenState extends State<StudentHomeScreen> {
  int _currentIndex = 0;
  List<dynamic> _myClasses = [];
  List<dynamic> _modules = [];
  List<dynamic> _attempts = [];
  bool _loading = false;

  // ChemBot AI
  final _aiCtrl = TextEditingController();
  final List<Map<String, String>> _aiMessages = [];
  bool _aiLoading = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _loading = true);
    final cls = await ApiService.getClasses(myClasses: true);
    final mods = await ApiService.getModules();
    final atts = await ApiService.getAttempts();
    if (mounted) {
      setState(() {
        _myClasses = cls;
        _modules = mods;
        _attempts = atts;
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

  void _showJoinClassDialog() {
    final codeCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Gabung Kelas Kimia'),
        content: TextField(
          controller: codeCtrl,
          textCapitalization: TextCapitalization.characters,
          decoration: const InputDecoration(labelText: 'Kode Kelas dari Guru'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Batal')),
          ElevatedButton(
            onPressed: () async {
              if (codeCtrl.text.isNotEmpty) {
                final res = await ApiService.joinClass(codeCtrl.text.trim());
                Navigator.pop(ctx);
                if (res['ok']) {
                  _loadData();
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Kode kelas tidak valid atau sudah bergabung')),
                  );
                }
              }
            },
            child: const Text('Gabung'),
          ),
        ],
      ),
    );
  }

  Future<void> _sendChemBot() async {
    final text = _aiCtrl.text.trim();
    if (text.isEmpty) return;
    setState(() {
      _aiMessages.add({'role': 'user', 'text': text});
      _aiCtrl.clear();
      _aiLoading = true;
    });

    try {
      final reply = await ApiService.askChemBot(text);
      setState(() {
        _aiMessages.add({'role': 'bot', 'text': reply});
      });
    } catch (e) {
      setState(() {
        _aiMessages.add({'role': 'bot', 'text': 'Gagal menjawab: ${e.toString()}'});
      });
    } finally {
      if (mounted) setState(() => _aiLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF6F8FC),
      appBar: AppBar(
        title: Text('Siswa - ${widget.user.fullName}'),
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
          : [
              _buildModulesTab(),
              _buildClassesTab(),
              _buildChemBotTab(),
            ][_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (idx) => setState(() => _currentIndex = idx),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.menu_book_outlined),
            selectedIcon: Icon(Icons.menu_book),
            label: 'Materi & Lab',
          ),
          NavigationDestination(
            icon: Icon(Icons.class_outlined),
            selectedIcon: Icon(Icons.class_),
            label: 'Kelasku',
          ),
          NavigationDestination(
            icon: Icon(Icons.smart_toy_outlined),
            selectedIcon: Icon(Icons.smart_toy),
            label: 'KimiBot AI',
          ),
        ],
      ),
    );
  }

  Widget _buildModulesTab() {
    if (_modules.isEmpty) {
      return const Center(child: Text('Belum ada modul materi'));
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _modules.length,
      itemBuilder: (ctx, i) {
        final m = _modules[i];
        final materials = (m['materials'] as List?) ?? [];
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ExpansionTile(
            leading: CircleAvatar(
              backgroundColor: Colors.purple.shade100,
              child: const Icon(Icons.science, color: Colors.purple),
            ),
            title: Text(m['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
            subtitle: Text('Kelas ${m['grade_level']} • ${materials.length} topik'),
            children: materials.map<Widget>((mat) {
              return ListTile(
                leading: const Icon(Icons.article_outlined, size: 20),
                title: Text(mat['title'] ?? ''),
                trailing: const Icon(Icons.chevron_right, size: 18),
                onTap: () {
                  showModalBottomSheet(
                    context: context,
                    isScrollControlled: true,
                    shape: const RoundedRectangleBorder(
                      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
                    ),
                    builder: (_) => Container(
                      padding: const EdgeInsets.all(24),
                      height: MediaQuery.of(context).size.height * 0.75,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            mat['title'] ?? '',
                            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                          ),
                          const Divider(height: 24),
                          Expanded(
                            child: SingleChildScrollView(
                              child: Text(
                                mat['content_text'] ?? mat['content_html'] ?? 'Konten materi belum tersedia.',
                                style: const TextStyle(fontSize: 14, height: 1.6),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              );
            }).toList(),
          ),
        );
      },
    );
  }

  Widget _buildClassesTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Kelas yang Diikuti', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
              ElevatedButton.icon(
                onPressed: _showJoinClassDialog,
                icon: const Icon(Icons.add, size: 18),
                label: const Text('Gabung Kelas'),
              ),
            ],
          ),
        ),
        Expanded(
          child: _myClasses.isEmpty
              ? const Center(child: Text('Belum bergabung dengan kelas manapun'))
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  itemCount: _myClasses.length,
                  itemBuilder: (ctx, i) {
                    final c = _myClasses[i];
                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Colors.blue.shade100,
                          child: Text(c['grade_level'] ?? 'X'),
                        ),
                        title: Text(c['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text('Guru: ${c['teacher_name'] ?? '-'}'),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }

  Widget _buildChemBotTab() {
    return Column(
      children: [
        Expanded(
          child: _aiMessages.isEmpty
              ? Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.smart_toy, size: 48, color: Colors.blue.shade300),
                      const SizedBox(height: 12),
                      const Text(
                        'Tanya materi atau reaksi kimia ke KimiBot!',
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _aiMessages.length,
                  itemBuilder: (ctx, i) {
                    final m = _aiMessages[i];
                    final isUser = m['role'] == 'user';
                    return Align(
                      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(12),
                        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                        decoration: BoxDecoration(
                          color: isUser ? Colors.blueAccent : Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.04),
                              blurRadius: 4,
                              offset: const Offset(0, 2),
                            ),
                          ],
                        ),
                        child: Text(
                          m['text'] ?? '',
                          style: TextStyle(
                            color: isUser ? Colors.white : Colors.black87,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
        if (_aiLoading)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 8),
            child: LinearProgressIndicator(),
          ),
        Container(
          padding: const EdgeInsets.all(12),
          color: Colors.white,
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _aiCtrl,
                  decoration: const InputDecoration(
                    hintText: 'Tanyakan rumus atau konsep kimia...',
                    border: InputBorder.none,
                  ),
                  onSubmitted: (_) => _sendChemBot(),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.send, color: Colors.blueAccent),
                onPressed: _sendChemBot,
              ),
            ],
          ),
        ),
      ],
    );
  }
}
