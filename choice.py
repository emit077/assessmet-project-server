import keys

""" user account type """
ACCOUNT_TYPE_CHOICES = [
    (keys.SUPER_ADMIN, keys.SUPER_ADMIN),
    (keys.ADMIN, keys.ADMIN),
    (keys.CUSTOMER, keys.CUSTOMER),
]
""" user gender options """
GENDER_CHOICES = [
    (keys.MALE, keys.MALE),
    (keys.FEMALE, keys.FEMALE),
    (keys.TRANSGENDER, keys.TRANSGENDER),
]