from django.db import models
from django.contrib.auth.models import User

class Character(models.Model):
    CLASS_CHOICES = [
        ('Warlock', 'Warlock'),
        ('Paladin', 'Paladin'),
        ('Shaman', 'Shaman'),
        ('Mage', 'Mage'),
        ('Druid', 'Druid'),
        ('Warrior', 'Warrior'),
    ]

    POSITION_CHOICES = [
        ('Tank', 'Tank'),
        ('Heal', 'Heal'),
        ('Melee_Dps', 'Melee DPS'),
        ('Ranged_Dps', 'Ranged DPS'),
    ]

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    character_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = False)  # Link to User model

    def __str__(self):
        return f"{self.name} - {self.character_class} - {self.position}"
