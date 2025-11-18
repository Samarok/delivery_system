import 'package:flutter/material.dart';
import 'services/api_service.dart';
import 'models/delivery.dart';
import 'models/sensor_data.dart';

class DispatcherHomeScreen extends StatefulWidget {
  @override
  _DispatcherHomeScreenState createState() => _DispatcherHomeScreenState();
}

class _DispatcherHomeScreenState extends State<DispatcherHomeScreen> {
  final ApiService _apiService = ApiService();
  List<Delivery> _deliveries = [];
  List<SensorData> _temperatureData = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      await _apiService.login('dispatcher1', 'password');
      final deliveries = await _apiService.getDeliveries();
      final tempData = await _apiService.getTemperatureData();
      setState(() {
        _deliveries = deliveries;
        _temperatureData = tempData;
        _isLoading = false;
      });
    } catch (e) {
      print('Error: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildTemperatureAlert(double temperature) {
    if (temperature > 8.0) {
      return Row(
        children: [
          Icon(Icons.warning, color: Colors.red),
          SizedBox(width: 4),
          Text('HIGH TEMP!', style: TextStyle(color: Colors.red)),
        ],
      );
    }
    return SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Dispatcher App'),
        backgroundColor: Colors.orange,
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadData,
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'Temperature Monitoring',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                  Container(
                    height: 120,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _temperatureData.length,
                      itemBuilder: (context, index) {
                        final data = _temperatureData[index];
                        return Container(
                          width: 150,
                          margin: EdgeInsets.all(8),
                          padding: EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: data.temperature > 8.0 ? Colors.red[100] : Colors.green[100],
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.grey),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                '${data.temperature}°C',
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color: data.temperature > 8.0 ? Colors.red : Colors.green,
                                ),
                              ),
                              Text('Sensor ${data.sensorId}'),
                              _buildTemperatureAlert(data.temperature),
                            ],
                          ),
                        );
                      },
                    ),
                  ),
                  Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'All Deliveries',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                  ),
                  ListView.builder(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(),
                    itemCount: _deliveries.length,
                    itemBuilder: (context, index) {
                      final delivery = _deliveries[index];
                      return Card(
                        margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                        color: _getStatusColor(delivery.status),
                        child: ListTile(
                          title: Text('Delivery #${delivery.id}'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Driver: ${delivery.driverName}'),
                              Text('Receiver: ${delivery.receiverName}'),
                              Text('Temp: ${delivery.currentTemperature}°C'),
                            ],
                          ),
                          trailing: Chip(
                            label: Text(
                              delivery.status.toUpperCase(),
                              style: TextStyle(color: Colors.white, fontSize: 12),
                            ),
                            backgroundColor: _getStatusChipColor(delivery.status),
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'pending': return Colors.grey[100]!;
      case 'in_transit': return Colors.blue[50]!;
      case 'delivered': return Colors.orange[50]!;
      case 'completed': return Colors.green[50]!;
      default: return Colors.white;
    }
  }

  Color _getStatusChipColor(String status) {
    switch (status) {
      case 'pending': return Colors.grey;
      case 'in_transit': return Colors.blue;
      case 'delivered': return Colors.orange;
      case 'completed': return Colors.green;
      default: return Colors.grey;
    }
  }
}
