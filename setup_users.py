import os
import django

# Weka mazingira ya Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pharmacy_system.settings")
django.setup()

from django.contrib.auth.models import User, Group

accounts = [
    ("employee1", "EMPLOYEE"),
    ("employee2", "EMPLOYEE"),
    ("boss", "BOSS"),
    ("supplier", "SUPPLIER"),
    ("systemadmin", "ADMIN"),
]

for username, role_name in accounts:
    group, _ = Group.objects.get_or_create(name=role_name)
    user, _ = User.objects.get_or_create(username=username)
    user.set_password("1234")
    
    if role_name == "ADMIN":
        user.is_staff = True
        user.is_superuser = True
        
    user.save()
    user.groups.set([group])
    print(f"✅ User '{username}' na role '{role_name}' imewekewa password: 1234")

print("\nUsers wote wamewekwa kikamilifu!")