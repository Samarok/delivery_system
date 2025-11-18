class SensorData {
  final int id;
  final double temperature;
  final DateTime timestamp;
  final String sensorId;

  SensorData({
    required this.id,
    required this.temperature,
    required this.timestamp,
    required this.sensorId,
  });

  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      id: json['id'],
      temperature: json['temperature'].toDouble(),
      timestamp: DateTime.parse(json['timestamp']),
      sensorId: json['sensor_id'],
    );
  }
}
