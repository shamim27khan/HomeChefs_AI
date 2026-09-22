import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../config/theme.dart';
import '../models/daily_meal.dart';
import '../services/chef_service.dart';
import '../widgets/app_logo.dart';
import '../widgets/error_message.dart';
import '../widgets/loading_indicator.dart';
import '../widgets/meal_card.dart';
import 'meal_detail_screen.dart';

class MealsTab extends StatefulWidget {
  const MealsTab({super.key});

  @override
  State<MealsTab> createState() => _MealsTabState();
}

class _MealsTabState extends State<MealsTab> with AutomaticKeepAliveClientMixin {
  final ChefService _service = ChefService();
  List<DailyMeal> _meals = [];
  bool _isLoading = false;
  bool _locationRequested = false;
  String? _error;
  String? _locationStatus;
  double _radius = 3.0;
  Position? _position;

  @override
  bool get wantKeepAlive => true;

  Future<void> _useMyLocation() async {
    setState(() {
      _isLoading = true;
      _error = null;
      _locationStatus = 'Getting your location...';
    });
    try {
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      if (!serviceEnabled) {
        throw Exception('Location services are disabled. Please enable GPS.');
      }
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw Exception('Location permission denied.');
      }
      _position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(accuracy: LocationAccuracy.medium),
      );
      _locationRequested = true;
      await _loadNearby();
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
          _locationStatus = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  Future<void> _loadNearby() async {
    if (_position == null) return;
    setState(() {
      _isLoading = true;
      _error = null;
      _locationStatus = 'Finding dishes near you...';
    });
    try {
      final result = await _service.getNearbyDishes(
        latitude: _position!.latitude,
        longitude: _position!.longitude,
        radius: _radius,
      );
      final dishes = (result['dishes'] as List<dynamic>)
          .map((e) => DailyMeal.fromJson(e as Map<String, dynamic>))
          .toList();
      if (mounted) {
        setState(() {
          _meals = dishes;
          _locationStatus = '${result['total_found']} dishes found within ${_radius.toStringAsFixed(0)} km';
        });
      }
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
      backgroundColor: AppColors.lightBg,
      appBar: brandedAppBar(
        automaticallyImplyLeading: false,
        actions: [
          if (_locationRequested)
            IconButton(icon: const Icon(Icons.refresh), onPressed: _loadNearby),
        ],
      ),
      body: Column(
        children: [
          // Hero banner (mirrors the web hero-section gradient)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.fromLTRB(16, 20, 16, 20),
            decoration: const BoxDecoration(gradient: AppColors.heroGradient),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Text(
                  'Dishes Near Me',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Fresh homemade food from chefs around you',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isLoading ? null : _useMyLocation,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: AppColors.primary,
                    ),
                    icon: const Icon(Icons.my_location),
                    label: const Text('Use My Current Location'),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.radar, color: Colors.white70, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: SliderTheme(
                        data: SliderTheme.of(context).copyWith(
                          activeTrackColor: Colors.white,
                          inactiveTrackColor: Colors.white38,
                          thumbColor: Colors.white,
                          overlayColor: Colors.white24,
                        ),
                        child: Slider(
                          value: _radius,
                          min: 1,
                          max: 20,
                          divisions: 19,
                          onChanged: (v) => setState(() => _radius = v),
                          onChangeEnd: (_) {
                            if (_position != null) _loadNearby();
                          },
                        ),
                      ),
                    ),
                    Text(
                      '${_radius.toStringAsFixed(0)} km',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
                if (_locationStatus != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      _locationStatus!,
                      style: const TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? const LoadingIndicator()
                : _error != null
                    ? ErrorMessage(message: _error!, onRetry: _loadNearby)
                    : !_locationRequested
                        ? ListView(
                            padding: const EdgeInsets.all(24),
                            children: [
                              const Text(
                                'Click "Use My Current Location" to find nearby dishes',
                                textAlign: TextAlign.center,
                                style: TextStyle(color: Colors.black54),
                              ),
                              const SizedBox(height: 32),
                              const Center(child: SectionTitle('How It Works')),
                              const SizedBox(height: 20),
                              _howItWorksStep(Icons.restaurant, 'Chefs Cook Daily',
                                  'Home chefs cook what they already make for their families, just with extra portions'),
                              _howItWorksStep(Icons.phone_android, 'You Order',
                                  'Browse today\'s menu and order before the cutoff time'),
                              _howItWorksStep(Icons.sentiment_satisfied_alt, 'Enjoy Fresh Food',
                                  'Pickup or get delivery of homemade, hygienic food'),
                            ],
                          )
                        : _meals.isEmpty
                            ? const Center(child: Text('No dishes found nearby. Try increasing the radius.'))
                            : ListView.builder(
                                itemCount: _meals.length,
                                itemBuilder: (context, index) => MealCard(
                                  meal: _meals[index],
                                  onTap: () => Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => MealDetailScreen(meal: _meals[index])),
                                  ),
                                ),
                              ),
          ),
        ],
      ),
    );
  }

  Widget _howItWorksStep(IconData icon, String title, String description) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.primary, AppColors.primaryLight],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: Colors.white, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 15,
                        color: AppColors.secondary)),
                const SizedBox(height: 4),
                Text(description,
                    style: const TextStyle(color: Colors.black54, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}