from django.contrib.auth.hashers import identify_hasher, make_password
from django.db import migrations


def hash_plaintext_passwords(apps, schema_editor):
    """Convert legacy plain-text passwords to Django password hashes."""
    Customer = apps.get_model('delivery', 'Customer')
    for customer in Customer.objects.all().iterator():
        password = customer.password or ''
        try:
            identify_hasher(password)
        except ValueError:
            customer.password = make_password(password)
            customer.save(update_fields=['password'])


class Migration(migrations.Migration):

    dependencies = [
        ('delivery', '0011_alter_customer_options_alter_customer_managers_and_more'),
    ]

    operations = [
        migrations.RunPython(hash_plaintext_passwords, migrations.RunPython.noop),
    ]
