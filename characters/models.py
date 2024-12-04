from django.db import models

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

    def __str__(self):
        return f"{self.name} - {self.character_class} - {self.position}"
