from django.db import models


class CustomPosition (models.TextChoices):
        INTERN = 'intern'
        PROBATION = 'probation'
        PERMANANT = 'permanent'

class Status (models.TextChoices):
        ABSENT = 'absent'
        PRESENT = 'present'
        HALF_LEAVE = 'half_leave'

class UserRole (models.TextChoices):
        DEVELOPER = 'developer'
        MANAGER = 'manager'
        ADMIN = 'admin'
        TEAM_LEAD = 'team_lead'
 