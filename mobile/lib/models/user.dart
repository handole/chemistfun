class User {
  final int id;
  final String uuid;
  final String email;
  final String fullName;
  final String role; // 'teacher' atau 'student'

  User({
    required this.id,
    required this.uuid,
    required this.email,
    required this.fullName,
    required this.role,
  });

  bool get isTeacher => role == 'teacher';
  bool get isStudent => role == 'student';

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      uuid: json['uuid'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      role: json['role'] ?? 'student',
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'uuid': uuid,
    'email': email,
    'full_name': fullName,
    'role': role,
  };
}
