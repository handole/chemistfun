import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'api_config.dart';
import '../models/user.dart';

class ApiService {
  static const _tokenKey = 'kimifun_token';
  static const _userKey = 'kimifun_user';

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<User?> getCurrentUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userStr = prefs.getString(_userKey);
    if (userStr == null) return null;
    return User.fromJson(jsonDecode(userStr));
  }

  static Future<void> saveSession(String token, User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  static Future<void> clearSession() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  static Future<Map<String, String>> _headers() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  // Auth
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode == 200) {
      final user = User.fromJson(data['user']);
      await saveSession(data['access_token'], user);
      return {'ok': true, 'user': user};
    }
    return {'ok': false, 'message': data['detail'] ?? 'Login gagal'};
  }

  static Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    required String role,
    String? teacherInviteCode,
  }) async {
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': fullName,
        'role': role,
        if (teacherInviteCode != null && teacherInviteCode.isNotEmpty)
          'teacher_invite_code': teacherInviteCode,
      }),
    );
    final data = jsonDecode(res.body);
    if (res.statusCode == 201) {
      final user = User.fromJson(data['user']);
      await saveSession(data['access_token'], user);
      return {'ok': true, 'user': user};
    }
    return {'ok': false, 'message': data['detail'] ?? 'Pendaftaran gagal'};
  }

  // Classes
  static Future<List<dynamic>> getClasses({bool myClasses = false}) async {
    final headers = await _headers();
    final res = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/classes/?my_classes=$myClasses'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return [];
  }

  static Future<Map<String, dynamic>> createClass(String name, String gradeLevel) async {
    final headers = await _headers();
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/classes/'),
      headers: headers,
      body: jsonEncode({'name': name, 'grade_level': gradeLevel}),
    );
    return {'ok': res.statusCode == 201, 'data': jsonDecode(res.body)};
  }

  static Future<Map<String, dynamic>> joinClass(String classCode) async {
    final headers = await _headers();
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/classes/join'),
      headers: headers,
      body: jsonEncode({'class_code': classCode}),
    );
    return {'ok': res.statusCode == 200, 'data': jsonDecode(res.body)};
  }

  // Modules & Content
  static Future<List<dynamic>> getModules({String? gradeLevel}) async {
    final headers = await _headers();
    final url = gradeLevel != null
        ? '${ApiConfig.baseUrl}/content/modules?grade_level=$gradeLevel'
        : '${ApiConfig.baseUrl}/content/modules';
    final res = await http.get(Uri.parse(url), headers: headers);
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return [];
  }

  // Journals (Teacher)
  static Future<List<dynamic>> getJournals({int? classId}) async {
    final headers = await _headers();
    final url = classId != null
        ? '${ApiConfig.baseUrl}/journals/?class_id=$classId'
        : '${ApiConfig.baseUrl}/journals/';
    final res = await http.get(Uri.parse(url), headers: headers);
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return [];
  }

  static Future<Map<String, dynamic>> createJournal(Map<String, dynamic> payload) async {
    final headers = await _headers();
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/journals/'),
      headers: headers,
      body: jsonEncode(payload),
    );
    return {'ok': res.statusCode == 201, 'data': jsonDecode(res.body)};
  }

  // Quizzes & Assessment
  static Future<List<dynamic>> getAttempts() async {
    final headers = await _headers();
    final res = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/assessment/attempts'),
      headers: headers,
    );
    if (res.statusCode == 200) {
      return jsonDecode(res.body);
    }
    return [];
  }

  // ChemBot AI
  static Future<String> askChemBot(String question) async {
    final headers = await _headers();
    final res = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/content/ask-chembot'),
      headers: headers,
      body: jsonEncode({'question': question}),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      return data['answer'] ?? '';
    }
    final err = jsonDecode(res.body);
    throw Exception(err['detail'] ?? 'Gagal menghubungi ChemBot');
  }
}
