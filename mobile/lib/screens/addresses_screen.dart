import 'package:flutter/material.dart';
import '../models/address.dart';
import '../services/customer_service.dart';
import '../widgets/address_card.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import 'add_address_screen.dart';

class AddressesScreen extends StatefulWidget {
  const AddressesScreen({super.key});

  @override
  State<AddressesScreen> createState() => _AddressesScreenState();
}

class _AddressesScreenState extends State<AddressesScreen> {
  final CustomerService _service = CustomerService();
  List<Address> _addresses = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAddresses();
  }

  Future<void> _loadAddresses() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final addresses = await _service.getAddresses();
      if (mounted) setState(() => _addresses = addresses);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Addresses'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const AddAddressScreen())).then((_) => _loadAddresses())),
        ],
      ),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadAddresses)
              : _addresses.isEmpty
                  ? const Center(child: Text('No addresses saved.'))
                  : ListView.builder(
                      itemCount: _addresses.length,
                      itemBuilder: (context, index) => AddressCard(address: _addresses[index]),
                    ),
    );
  }
}
