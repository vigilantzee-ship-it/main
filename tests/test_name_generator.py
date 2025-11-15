"""
Tests for the creature name generator.
"""

import unittest
from src.utils.name_generator import NameGenerator, generate_name


class TestNameGenerator(unittest.TestCase):
    """Test the NameGenerator class."""
    
    def test_generator_initialization(self):
        """Test creating a name generator."""
        gen = NameGenerator()
        self.assertIsNotNone(gen)
        
        # Test with seed
        gen_seeded = NameGenerator(seed=42)
        self.assertIsNotNone(gen_seeded)
    
    def test_generate_single_name(self):
        """Test generating a single name."""
        gen = NameGenerator()
        name = gen.generate()
        
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        self.assertTrue(name[0].isupper(), "Name should start with capital letter")
    
    def test_generate_with_seed_reproducibility(self):
        """Test that seeded generators produce same names."""
        gen1 = NameGenerator(seed=123)
        gen2 = NameGenerator(seed=123)
        
        names1 = [gen1.generate() for _ in range(10)]
        names2 = [gen2.generate() for _ in range(10)]
        
        self.assertEqual(names1, names2, "Seeded generators should produce same names")
    
    def test_generate_batch(self):
        """Test generating multiple names."""
        gen = NameGenerator()
        count = 20
        names = gen.generate_batch(count)
        
        self.assertEqual(len(names), count)
        for name in names:
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)
    
    def test_generate_batch_unique(self):
        """Test that unique batch generates unique names."""
        gen = NameGenerator(seed=42)
        count = 30
        names = gen.generate_batch(count, unique=True)
        
        # All names should be unique
        self.assertEqual(len(names), len(set(names)), "Names should be unique")
    
    def test_generate_batch_non_unique(self):
        """Test that non-unique batch can have duplicates."""
        gen = NameGenerator(seed=42)
        count = 50
        names = gen.generate_batch(count, unique=False)
        
        # Should have generated the requested count
        self.assertEqual(len(names), count)
    
    def test_syllable_variation(self):
        """Test that different syllable counts work."""
        gen = NameGenerator()
        
        # Test 2-syllable names
        name2 = gen.generate(min_syllables=2, max_syllables=2)
        self.assertIsInstance(name2, str)
        
        # Test 3-syllable names
        name3 = gen.generate(min_syllables=3, max_syllables=3)
        self.assertIsInstance(name3, str)
    
    def test_module_level_function(self):
        """Test the module-level generate_name function."""
        name = generate_name()
        self.assertIsInstance(name, str)
        self.assertGreater(len(name), 0)
        self.assertTrue(name[0].isupper())
    
    def test_name_variety(self):
        """Test that generator produces varied names."""
        gen = NameGenerator()
        names = gen.generate_batch(50, unique=True)
        
        # With 50 names, we should have good variety
        self.assertGreater(len(set(names)), 40, "Should produce varied names")


if __name__ == '__main__':
    unittest.main()
