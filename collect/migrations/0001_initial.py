from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("bd_models", "0014_alter_ball_options_alter_ballinstance_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name='Collectible',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requirement_type', models.CharField(blank=True, choices=[('total', 'Total Balls Owned'), ('shiny', 'Shiny Balls Owned'), ('ball', 'Specific Ball (1 required)'), ('balls', 'Specific Ball (X required)'), ('special', 'Special Card Ball')], max_length=50, null=True)),
                ('requirement_value', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('emoji', models.CharField(max_length=100)),
                ('cost', models.IntegerField()),
                ('bio', models.TextField(blank=True, null=True)),
                ('image_url', models.CharField(blank=True, max_length=300, null=True)),
            ],
            options={
                'db_table': 'collectible',
                'verbose_name': 'Collectible',
                'verbose_name_plural': 'Collectibles',
            },
        ),
        migrations.CreateModel(
            name='PlayerCollectible',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obtained_at', models.DateTimeField(auto_now_add=True)),
                ('collectible', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='owners', to='collect.Collectible')),
                ('player', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='collectibles', to='bd_models.player')),
            ],
            options={
                'db_table': 'playercollectible',
                'unique_together': {('player', 'collectible')},
                'indexes': [
                    models.Index(fields=['player'], name='playercollectible_player_idx'),
                    models.Index(fields=['collectible'], name='playercollectible_collectible_idx'),
                ],
            },
        ),
    ]
