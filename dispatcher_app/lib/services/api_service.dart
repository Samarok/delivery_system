import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/sensor_data.dart';
import '../models/delivery.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000/api';
  String? _token;

  Future<void> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},  // ← ДОБАВИТЬ
      body: json.encode({  // ← ИСПОЛЬЗОВАТЬ json.encode
        'username': username,
       'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['access_token'];
    } else {
      throw Exception('Login failed');
    }
  }

  Future<List<SensorData>> getTemperatureData() async {
    final response = await http.get(
      Uri.parse('$baseUrl/sensors/temperature'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => SensorData.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load temperature data');
    }
  }

  Future<List<Delivery>> getDeliveries() async {
    final response = await http.get(
      Uri.parse('$baseUrl/deliveries'),
      headers: {'Authorization': 'Bearer $_token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Delivery.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load deliveries');
    }
  }

  Future<void> updateDeliveryStatus(int deliveryId, String status) async {
    final response = await http.put(
      Uri.parse('$baseUrl/deliveries/$deliveryId'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
      body: json.encode({'status': status}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update delivery status');
    }
  }
}
