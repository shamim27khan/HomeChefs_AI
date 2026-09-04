import 'package:flutter/material.dart';
import '../models/chef.dart';
import '../services/chef_service.dart';
import '../widgets/chef_card.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import 'chef_detail_screen.dart';

class ChefsTab extends StatefulWidget {
  const ChefsTab({super.key});

  @override
  State<ChefsTab> createState() => _ChefsTabState();
}

class _ChefsTabState extends State<ChefsTab> with AutomaticKeepAliveClientMixin {
  final ChefService _service = ChefService();
  List<Chef> _chefs = [];
  bool _isLoading = true;
  String? _error;
  final _searchController = TextEditingController();

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadChefs();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadChefs() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final chefs = await _service.getPublicChefs(search: _searchController.text.trim());
      if (mounted) setState(() => _chefs = chefs);
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(title: const Text('Browse Chefs')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(12.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                labelText: 'Search chefs or cuisine',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(icon: const Icon(Icons.clear), onPressed: () => _searchController.clear()),
                border: const OutlineInputBorder(),
              ),
              onSubmitted: (_) => _loadChefs(),
            ),
          ),
          Expanded(
            child: _isLoading
                ? const LoadingIndicator()
                : _error != null
                    ? ErrorMessage(message: _error!, onRetry: _loadChefs)
                    : _chefs.isEmpty
                        ? const Center(child: Text('No chefs found.'))
                        : ListView.builder(
                            itemCount: _chefs.length,
                            itemBuilder: (context, index) => ChefCard(
                              chef: _chefs[index],
                              onTap: () => Navigator.of(context).push(
                                MaterialPageRoute(builder: (_) => ChefDetailScreen(chef: _chefs[index])),
                              ),
                            ),
                          ),
          ),
        ],
      ),
    );
  }
}
