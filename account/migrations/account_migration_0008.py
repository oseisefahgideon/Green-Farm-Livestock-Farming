from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_alter_farm_farm_logo_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='farm_email',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
