import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/delivery.dart';

class DriverHomeScreen extends StatefulWidget {
  @override
  _DriverHomeScreenState createState() => _DriverHomeScreenState();
}

class _DriverHomeScreenState extends State<DriverHomeScreen> {
  final ApiService _apiService = ApiService();
  List<Delivery> _deliveries = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      await _apiService.login('driver1', 'password');
      final deliveries = await _apiService.getDeliveries();
      setState(() {
        _deliveries = deliveries;
        _isLoading = false;
      });
    } catch (e) {
      print('Error: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _updateStatus(int deliveryId, String status) async {
    try {
      await _apiService.updateDeliveryStatus(deliveryId, status);
      await _loadData(); // Reload data
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status updated to $status')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to update status')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Driver App'),
        backgroundColor: Colors.blue,
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : ListView.builder(
              itemCount: _deliveries.length,
              itemBuilder: (context, index) {
                final delivery = _deliveries[index];
                return Card(
                  margin: EdgeInsets.all(8),
                  child: ListTile(
                    title: Text('Delivery #${delivery.id}'),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Status: ${delivery.status}'),
                        Text('Temperature: ${delivery.currentTemperature}°C'),
                        Text('Receiver: ${delivery.receiverName}'),
                      ],
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        if (delivery.status == 'pending')
                          IconButton(
                            icon: Icon(Icons.check, color: Colors.green),
                            onPressed: () => _updateStatus(delivery.id, 'in_transit'),
                          ),
                        if (delivery.status == 'in_transit')
                          IconButton(
                            icon: Icon(Icons.delivery_dining, color: Colors.orange),
                            onPressed: () => _updateStatus(delivery.id, 'delivered'),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
