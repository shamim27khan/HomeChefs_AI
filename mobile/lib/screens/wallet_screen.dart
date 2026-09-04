import 'package:flutter/material.dart';
import '../services/payment_service.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  final PaymentService _service = PaymentService();
  Map<String, dynamic>? _wallet;
  List<Map<String, dynamic>> _transactions = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadWallet();
  }

  Future<void> _loadWallet() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      _wallet = await _service.getWallet();
      _transactions = await _service.getWalletTransactions();
    } catch (e) {
      _error = e.toString();
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Wallet')),
      body: _isLoading
          ? const LoadingIndicator()
          : _error != null
              ? ErrorMessage(message: _error!, onRetry: _loadWallet)
              : Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(16.0),
                          child: Row(
                            children: [
                              const Icon(Icons.account_balance_wallet, size: 40),
                              const SizedBox(width: 16),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Wallet Balance'),
                                  Text(
                                    '₹${_wallet?['balance'] ?? 0.00}',
                                    style: Theme.of(context).textTheme.headlineSmall,
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),
                      const Text('Transactions', style: TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Expanded(
                        child: _transactions.isEmpty
                            ? const Center(child: Text('No transactions yet.'))
                            : ListView.builder(
                                itemCount: _transactions.length,
                                itemBuilder: (context, index) {
                                  final t = _transactions[index];
                                  return ListTile(
                                    leading: Icon(t['transaction_type'] == 'credit' ? Icons.arrow_downward : Icons.arrow_upward,
                                        color: t['transaction_type'] == 'credit' ? Colors.green : Colors.red),
                                    title: Text(t['description'] ?? 'Transaction'),
                                    subtitle: Text('${t['transaction_id'] ?? ''}'),
                                    trailing: Text('₹${t['amount'] ?? 0}'),
                                  );
                                },
                              ),
                      ),
                    ],
                  ),
                ),
    );
  }
}
