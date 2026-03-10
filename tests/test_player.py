import unittest
from classes.player import Player

class TestPlayerTakeDamage(unittest.TestCase):
    def setUp(self):
        self.player = Player("Test Player")
        # Base stats for con=10, level=1:
        # total_con = 10
        # max_hp = 10 * 10 + 1 * 5 = 105
        # defense = 10 * 2 = 20
        self.player.con = 10
        self.player.update_stats()
        self.player.hp = 100 # Reset HP to a known value

    def test_take_damage_greater_than_defense(self):
        # amount = 30, defense = 20
        # actual_damage = max(1, 30 - 20) = 10
        initial_hp = self.player.hp
        damage_taken = self.player.take_damage(30)

        self.assertEqual(damage_taken, 10)
        self.assertEqual(self.player.hp, initial_hp - 10)

    def test_take_damage_equal_to_defense(self):
        # amount = 20, defense = 20
        # actual_damage = max(1, 20 - 20) = 1
        initial_hp = self.player.hp
        damage_taken = self.player.take_damage(20)

        self.assertEqual(damage_taken, 1)
        self.assertEqual(self.player.hp, initial_hp - 1)

    def test_take_damage_less_than_defense(self):
        # amount = 5, defense = 20
        # actual_damage = max(1, 5 - 20) = 1
        initial_hp = self.player.hp
        damage_taken = self.player.take_damage(5)

        self.assertEqual(damage_taken, 1)
        self.assertEqual(self.player.hp, initial_hp - 1)

    def test_take_damage_reduces_hp_to_zero(self):
        # hp = 100, defense = 20
        # we want actual_damage = 100
        # amount - 20 = 100 => amount = 120
        damage_taken = self.player.take_damage(120)

        self.assertEqual(damage_taken, 100)
        self.assertEqual(self.player.hp, 0)

    def test_take_damage_clamped_at_zero_hp(self):
        # hp = 100, defense = 20
        # amount = 200 => actual_damage = 180
        damage_taken = self.player.take_damage(200)

        self.assertEqual(damage_taken, 180)
        self.assertEqual(self.player.hp, 0)

if __name__ == '__main__':
    unittest.main()
