# Generated by Django 4.1.1 on 2022-10-04 14:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0006_character_vector_column_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              CREATE TRIGGER vector_column_trigger
              BEFORE INSERT OR UPDATE OF name, description, vector_column
              ON characters_character
              FOR EACH ROW EXECUTE PROCEDURE
              tsvector_update_trigger(
                vector_column, 'pg_catalog.english', name, description
              );

              UPDATE characters_character SET vector_column = NULL;
            ''',

            reverse_sql='''
              DROP TRIGGER IF EXISTS vector_column_trigger
              ON characters_character;
            '''
        ),
    ]