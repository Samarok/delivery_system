class Delivery {
  final int id;
  final String status;
  final String driverName;
  final String receiverName;
  final double currentTemperature;
  final DateTime createdAt;

  Delivery({
    required this.id,
    required this.status,
    required this.driverName,
    required this.receiverName,
    required this.currentTemperature,
    required this.createdAt,
  });

  factory Delivery.fromJson(Map<String, dynamic> json) {
    return Delivery(
      id: json['id'],
      status: json['status'],
      driverName: json['driver_name'],
      receiverName: json['receiver_name'],
      currentTemperature: json['current_temperature'].toDouble(),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}
