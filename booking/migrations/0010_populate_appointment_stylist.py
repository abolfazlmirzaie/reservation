from django.db import migrations


def populate_appointment_stylist(apps, schema_editor):
    Appointment = apps.get_model("booking", "Appointment")

    appointments = Appointment.objects.select_related(
        "stylist_service"
    ).all()

    for appointment in appointments.iterator():
        appointment.stylist_id = appointment.stylist_service.stylist_id

        appointment.save(update_fields=["stylist"])


class Migration(migrations.Migration):

    dependencies = [
        ("booking", "0009_appointment_stylist_and_more"),
    ]

    operations = [
        migrations.RunPython(
            populate_appointment_stylist,
            migrations.RunPython.noop,
        ),
    ]