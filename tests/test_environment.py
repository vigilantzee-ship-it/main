"""
Unit tests for the environmental simulation system.

Tests weather, terrain, day/night cycles, and hazards.
"""

import unittest
import time
from src.models.environment import (
    Environment, WeatherConditions, WeatherType, TerrainType, TerrainCell,
    TimeOfDay, DayNightCycle, HazardType, EnvironmentalHazard
)
from src.models.spatial import Vector2D


class TestWeatherConditions(unittest.TestCase):
    """Test weather condition effects."""
    
    def test_weather_initialization(self):
        """Test creating weather conditions."""
        weather = WeatherConditions()
        self.assertEqual(weather.weather_type, WeatherType.CLEAR)
        self.assertEqual(weather.temperature, 20.0)
        self.assertEqual(weather.humidity, 0.5)
    
    def test_movement_modifier_clear(self):
        """Test movement modifier in clear weather."""
        weather = WeatherConditions(weather_type=WeatherType.CLEAR)
        modifier = weather.get_movement_modifier()
        self.assertGreaterEqual(modifier, 0.5)
        self.assertLessEqual(modifier, 1.2)
    
    def test_movement_modifier_stormy(self):
        """Test movement modifier in stormy weather."""
        weather = WeatherConditions(weather_type=WeatherType.STORMY)
        modifier = weather.get_movement_modifier()
        # Stormy weather should slow movement
        self.assertLess(modifier, 1.0)
    
    def test_hunger_modifier_cold(self):
        """Test hunger increases in cold weather."""
        weather = WeatherConditions(temperature=-5.0)
        modifier = weather.get_hunger_modifier()
        # Cold increases hunger
        self.assertGreater(modifier, 1.0)
    
    def test_hunger_modifier_hot(self):
        """Test hunger increases in hot weather."""
        weather = WeatherConditions(temperature=38.0)
        modifier = weather.get_hunger_modifier()
        # Heat increases hunger
        self.assertGreater(modifier, 1.0)
    
    def test_resource_quality_rainy(self):
        """Test resource quality improves in rain."""
        weather = WeatherConditions(weather_type=WeatherType.RAINY)
        modifier = weather.get_resource_quality_modifier()
        # Rain improves resources
        self.assertGreater(modifier, 1.0)
    
    def test_resource_quality_drought(self):
        """Test resource quality decreases in drought."""
        weather = WeatherConditions(weather_type=WeatherType.DROUGHT)
        modifier = weather.get_resource_quality_modifier()
        # Drought reduces resources
        self.assertLess(modifier, 1.0)


class TestTerrainCell(unittest.TestCase):
    """Test terrain cell properties."""
    
    def test_terrain_initialization(self):
        """Test creating terrain cell."""
        cell = TerrainCell(
            terrain_type=TerrainType.GRASS,
            position=Vector2D(10, 10)
        )
        self.assertEqual(cell.terrain_type, TerrainType.GRASS)
        self.assertEqual(cell.resource_richness, 1.0)
    
    def test_grass_movement(self):
        """Test grass has normal movement."""
        cell = TerrainCell(terrain_type=TerrainType.GRASS, position=Vector2D(0, 0))
        self.assertEqual(cell.get_movement_modifier(), 1.0)
    
    def test_water_movement(self):
        """Test water slows movement."""
        cell = TerrainCell(terrain_type=TerrainType.WATER, position=Vector2D(0, 0))
        modifier = cell.get_movement_modifier()
        # Water should slow movement significantly
        self.assertLess(modifier, 0.5)
    
    def test_desert_movement(self):
        """Test desert speeds movement."""
        cell = TerrainCell(terrain_type=TerrainType.DESERT, position=Vector2D(0, 0))
        modifier = cell.get_movement_modifier()
        # Desert should allow faster movement
        self.assertGreater(modifier, 1.0)
    
    def test_forest_visibility(self):
        """Test forest reduces visibility."""
        cell = TerrainCell(terrain_type=TerrainType.FOREST, position=Vector2D(0, 0))
        visibility = cell.get_visibility_modifier()
        # Forest should reduce visibility
        self.assertLess(visibility, 1.0)
    
    def test_forest_cover(self):
        """Test forest provides defensive cover."""
        cell = TerrainCell(terrain_type=TerrainType.FOREST, position=Vector2D(0, 0))
        cover = cell.get_cover_bonus()
        # Forest should provide the highest cover
        self.assertGreater(cover, 0.0)


class TestDayNightCycle(unittest.TestCase):
    """Test day/night cycle functionality."""
    
    def test_cycle_initialization(self):
        """Test creating day/night cycle."""
        cycle = DayNightCycle(cycle_duration=300.0, start_hour=7.0)
        self.assertEqual(cycle.cycle_duration, 300.0)
        self.assertEqual(cycle.start_hour, 7.0)
    
    def test_get_current_hour(self):
        """Test getting current hour."""
        cycle = DayNightCycle(start_hour=12.0)
        hour = cycle.get_current_hour()
        self.assertGreaterEqual(hour, 0.0)
        self.assertLess(hour, 24.0)
    
    def test_time_of_day_morning(self):
        """Test morning time of day."""
        cycle = DayNightCycle(start_hour=10.0)
        time_of_day = cycle.get_time_of_day()
        self.assertEqual(time_of_day, TimeOfDay.DAY)
    
    def test_visibility_day(self):
        """Test daytime visibility is maximum."""
        cycle = DayNightCycle(start_hour=12.0)
        visibility = cycle.get_visibility_modifier()
        self.assertEqual(visibility, 1.0)
    
    def test_visibility_night(self):
        """Test nighttime visibility is reduced."""
        cycle = DayNightCycle(start_hour=23.0)
        visibility = cycle.get_visibility_modifier()
        # Night should have reduced visibility
        self.assertLess(visibility, 1.0)
    
    def test_activity_day(self):
        """Test daytime activity is normal."""
        cycle = DayNightCycle(start_hour=12.0)
        activity = cycle.get_activity_modifier()
        self.assertEqual(activity, 1.0)
    
    def test_activity_night(self):
        """Test nighttime activity is reduced."""
        cycle = DayNightCycle(start_hour=23.0)
        activity = cycle.get_activity_modifier()
        # Night should reduce activity
        self.assertLess(activity, 1.0)


class TestEnvironmentalHazard(unittest.TestCase):
    """Test environmental hazards."""
    
    def test_hazard_initialization(self):
        """Test creating a hazard."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0,
            damage=5.0
        )
        self.assertEqual(hazard.hazard_type, HazardType.FIRE)
        self.assertEqual(hazard.radius, 10.0)
        self.assertEqual(hazard.damage, 5.0)
    
    def test_permanent_hazard_active(self):
        """Test permanent hazards are always active."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.THORNS,
            position=Vector2D(0, 0),
            duration=-1.0
        )
        self.assertTrue(hazard.is_active())
    
    def test_temporary_hazard_active(self):
        """Test temporary hazards expire."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.POISON_CLOUD,
            position=Vector2D(0, 0),
            duration=0.1  # 0.1 seconds
        )
        self.assertTrue(hazard.is_active())
        # Wait for it to expire
        time.sleep(0.15)
        self.assertFalse(hazard.is_active())
    
    def test_hazard_affects_position_inside(self):
        """Test hazard affects position inside radius."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0
        )
        # Position inside radius
        self.assertTrue(hazard.affects_position(Vector2D(52, 52)))
    
    def test_hazard_affects_position_outside(self):
        """Test hazard doesn't affect position outside radius."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0
        )
        # Position outside radius
        self.assertFalse(hazard.affects_position(Vector2D(100, 100)))
    
    def test_damage_at_center(self):
        """Test maximum damage at hazard center."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0,
            damage=10.0
        )
        # At center, damage should be maximum
        damage = hazard.get_damage_at_position(Vector2D(50, 50))
        self.assertEqual(damage, 10.0)
    
    def test_damage_at_edge(self):
        """Test reduced damage at hazard edge."""
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0,
            damage=10.0
        )
        # Just inside edge (distance ~8), damage should be minimal but non-zero
        damage = hazard.get_damage_at_position(Vector2D(58, 50))
        self.assertGreater(damage, 0.0)
        self.assertLess(damage, 10.0)


class TestEnvironment(unittest.TestCase):
    """Test complete environment system."""
    
    def test_environment_initialization(self):
        """Test creating an environment."""
        env = Environment(width=100.0, height=100.0)
        self.assertEqual(env.width, 100.0)
        self.assertEqual(env.height, 100.0)
        self.assertIsNotNone(env.weather)
        self.assertIsNotNone(env.day_night)
    
    def test_environment_without_weather(self):
        """Test environment without weather."""
        env = Environment(enable_weather=False)
        self.assertIsNone(env.weather)
    
    def test_environment_without_day_night(self):
        """Test environment without day/night cycle."""
        env = Environment(enable_day_night=False)
        self.assertIsNone(env.day_night)
    
    def test_terrain_grid_created(self):
        """Test terrain grid is populated."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        # Should have approximately 10x10 = 100 cells
        self.assertGreater(len(env.terrain_grid), 0)
    
    def test_get_terrain_at_position(self):
        """Test getting terrain at a position."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        terrain = env.get_terrain_at(Vector2D(25, 25))
        self.assertIsNotNone(terrain)
        self.assertIsInstance(terrain.terrain_type, TerrainType)
    
    def test_add_hazard(self):
        """Test adding a hazard."""
        env = Environment()
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50)
        )
        env.add_hazard(hazard)
        self.assertEqual(len(env.hazards), 1)
    
    def test_get_hazards_at_position(self):
        """Test getting hazards at a position."""
        env = Environment()
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0
        )
        env.add_hazard(hazard)
        
        # Position inside hazard
        hazards = env.get_hazards_at(Vector2D(52, 52))
        self.assertEqual(len(hazards), 1)
        
        # Position outside hazard
        hazards = env.get_hazards_at(Vector2D(100, 100))
        self.assertEqual(len(hazards), 0)
    
    def test_get_total_hazard_damage(self):
        """Test calculating total hazard damage."""
        env = Environment()
        hazard1 = EnvironmentalHazard(
            hazard_type=HazardType.FIRE,
            position=Vector2D(50, 50),
            radius=10.0,
            damage=5.0
        )
        hazard2 = EnvironmentalHazard(
            hazard_type=HazardType.POISON_CLOUD,
            position=Vector2D(52, 52),
            radius=10.0,
            damage=3.0
        )
        env.add_hazard(hazard1)
        env.add_hazard(hazard2)
        
        # Position affected by both hazards
        total_damage = env.get_total_hazard_damage(Vector2D(51, 51))
        self.assertGreater(total_damage, 0.0)
    
    def test_combined_movement_modifier(self):
        """Test combined movement modifier from weather and terrain."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        modifier = env.get_combined_movement_modifier(Vector2D(25, 25))
        self.assertGreater(modifier, 0.0)
        self.assertLessEqual(modifier, 2.0)
    
    def test_combined_visibility(self):
        """Test combined visibility from all sources."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        visibility = env.get_combined_visibility(Vector2D(25, 25))
        self.assertGreaterEqual(visibility, 0.0)
        self.assertLessEqual(visibility, 1.0)
    
    def test_resource_quality_at_position(self):
        """Test resource quality at a position."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        quality = env.get_resource_quality_at(Vector2D(25, 25))
        self.assertGreater(quality, 0.0)
    
    def test_defensive_cover(self):
        """Test getting defensive cover at position."""
        env = Environment(width=100.0, height=100.0, cell_size=10.0)
        cover = env.get_defensive_cover(Vector2D(25, 25))
        self.assertGreaterEqual(cover, 0.0)
        self.assertLessEqual(cover, 0.5)
    
    def test_environment_update(self):
        """Test environment update removes expired hazards."""
        env = Environment()
        # Add temporary hazard
        hazard = EnvironmentalHazard(
            hazard_type=HazardType.POISON_CLOUD,
            position=Vector2D(50, 50),
            duration=0.1
        )
        env.add_hazard(hazard)
        self.assertEqual(len(env.hazards), 1)
        
        # Wait for expiration
        time.sleep(0.15)
        env.update(0.1)
        
        # Hazard should be removed
        self.assertEqual(len(env.hazards), 0)
    
    def test_environment_serialization(self):
        """Test serializing environment to dict."""
        env = Environment()
        data = env.to_dict()
        
        self.assertIn('weather', data)
        self.assertIn('time_of_day', data)
        self.assertIn('active_hazards', data)


if __name__ == '__main__':
    unittest.main()
