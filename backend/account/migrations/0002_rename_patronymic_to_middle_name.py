from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile",
            old_name="patronymic",
            new_name="middle_name",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="has_no_patronymic",
            new_name="has_no_middle_name",
        ),
    ]
