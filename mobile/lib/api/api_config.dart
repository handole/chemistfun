class ApiConfig {
  // Ganti IP / host sesuai kebutuhan (10.0.2.2 untuk emulator android, localhost atau host tailscale)
  static const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api',
  );
}
