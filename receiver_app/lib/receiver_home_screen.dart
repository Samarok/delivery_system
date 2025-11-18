import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/delivery.dart';

class ReceiverHomeScreen extends StatefulWidget {
  @override
  _ReceiverHomeScreenState createState() => _ReceiverHomeScreenState();
}

class _ReceiverHomeScreenState extends State<ReceiverHomeScreen> {
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
      await _apiService.login('receiver1', 'password');
      final deliveries = await _apiService.getDeliveries();
      setState(() {
        _deliveries = deliveries.where((d) => d.status == 'delivered').toList();
        _isLoading = false;
      });
    } catch (e) {
      print('Error: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _confirmReceipt(int deliveryId) async {
    try {
      await _apiService.updateDeliveryStatus(deliveryId, 'completed');
      await _loadData();
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Delivery confirmed')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to confirm delivery')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Receiver App'),
        backgroundColor: Colors.green,
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : _deliveries.isEmpty
              ? Center(child: Text('No deliveries to receive'))
              : ListView.builder(
                  itemCount: _deliveries.length,
                  itemBuilder: (context, index) {
                    final delivery = _deliveries[index];
                    return Card(
                      margin: EdgeInsets.all(8),
                      child: ListTile(
                        leading: Icon(Icons.local_shipping, color: Colors.green),
                        title: Text('Delivery #${delivery.id}'),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Driver: ${delivery.driverName}'),
                            Text('Temperature: ${delivery.currentTemperature}°C'),
                            Text('Status: ${delivery.status}'),
                          ],
                        ),
                        trailing: ElevatedButton(
                          onPressed: () => _confirmReceipt(delivery.id),
                          child: Text('Confirm'),
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
