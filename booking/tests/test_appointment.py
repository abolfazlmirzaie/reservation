import threading
from concurrent.futures import ThreadPoolExecutor
from django.db import close_old_connections
from datetime import time, timedelta, datetime
from django.utils import timezone
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from booking.models import Appointment, PlatformSettings
from booking.services.slot_service import get_django_day_of_week
from booking.tasks import expire_pending_appointments
from salon.models import Salon, StylistService, Stylist, Service, SalonCategory, WorkingHours

User = get_user_model()

@pytest.fixture()
def customer(db):
    user = User.objects.create_user(
        phone_number="09334403225",
        password="slkhjgpoieshjrg",
        role="customer",
    )

    user.profile.first_name = "test"
    user.profile.last_name = "user"
    user.profile.save()
    return user


@pytest.fixture()
def salon_owner(db):
    return User.objects.create_user(
        phone_number="09334403226",
        password="slkhjgpoieshjrg",
        role="salon_owner",
    )


@pytest.fixture()
def stylist_user(db):
    return User.objects.create_user(
        phone_number="09334403254",
        password="slkhjgpoieshjrg",
        role="stylist",
    )

@pytest.fixture()
def stylist_user2(db):
    return User.objects.create_user(
        phone_number="09147895655",
        password="slkhjgpoieshjrg",
        role="stylist",
    )


@pytest.fixture()
def authenticated_client(customer):
    client = APIClient()
    client.force_authenticate(user=customer)
    return client

@pytest.fixture()
def salon(db , salon_owner):
    return Salon.objects.create(
        owner=salon_owner,
        name="سالن",
        name_en="salonExample",
        category="mens_salon",
        address="testaddress",
    )

@pytest.fixture()
def stylist(db, stylist_user, salon):
    return Stylist.objects.create(
        user=stylist_user,
        salon=salon,
        name="مهدی",
        name_en="stylistExample",
        phone="09653251414",
        booking_window_days=5,
    )



@pytest.fixture()
def stylist2(db, stylist_user2, salon):
    return Stylist.objects.create(
        user=stylist_user2,
        salon=salon,
        name="مهدی",
        name_en="stylistExample",
        phone="09654147558",
        booking_window_days=5,
    )

@pytest.fixture()
def service(db):
    return Service.objects.create(
        name="haircut"
    )

@pytest.fixture()
def stylist_service2(db, stylist2, service):
    return StylistService.objects.create(
        service=service,
        stylist=stylist2,
        price=500000,
        duration_minutes=30,
    )

@pytest.fixture()
def stylist_service(db, stylist, service):
    return StylistService.objects.create(
        service=service,
        stylist=stylist,
        price=500000,
        duration_minutes=30,
    )

@pytest.fixture
def appointment_time():
    return time(10, 0)


@pytest.fixture
def appointment_date():
    return timezone.localdate() + timedelta(days=1)


@pytest.fixture
def working_hours(stylist, appointment_date):
    return WorkingHours.objects.create(
        stylist=stylist,
        day_of_week=get_django_day_of_week(appointment_date.weekday()),
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_active=True,
    )

@pytest.fixture
def working_hours2(stylist2, appointment_date):
    return WorkingHours.objects.create(
        stylist=stylist2,
        day_of_week=get_django_day_of_week(appointment_date.weekday()),
        start_time=time(9, 0),
        end_time=time(17, 0),
        is_active=True,
    )


@pytest.fixture
def platform_settings(db):
    return PlatformSettings.objects.create(

    )



@pytest.mark.django_db
def test_success_reserve(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
    ):

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_201_CREATED



    appointment = Appointment.objects.get(id=response.data["appointment_id"])

    expected_time = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time),
    )


    assert appointment.status == "pending_payment"
    assert appointment.customer_name == "test user"
    assert appointment.customer_phone == customer.phone_number
    assert appointment.deposit_amount == 20000
    assert appointment.service_price_snapshot == 500000
    assert appointment.platform_share == 4000
    assert appointment.salon_share == 16000
    assert appointment.start_time == expected_time
    assert appointment.end_time == expected_time + timedelta(minutes=30)


@pytest.mark.django_db
def test_reservation_fails_when_date_is_outside_working_hours(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
):
    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": (appointment_date + timedelta(days=10)).isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert not Appointment.objects.filter(customer_phone=customer.phone_number).exists()




@pytest.mark.django_db
def test_reservation_fails_when_time_is_outside_working_hours(
        authenticated_client,
        appointment_date,
        stylist_service,
        working_hours,
        platform_settings,
        customer,
):


    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": time(23, 50).strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert not Appointment.objects.filter(customer_phone=customer.phone_number).exists()



@pytest.mark.django_db
def test_reservation_fails_when_stylist_is_inactive(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
        stylist
):

    stylist.is_active = False
    stylist.save()

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not Appointment.objects.filter(customer_phone=customer.phone_number).exists()





@pytest.mark.django_db
def test_reservation_fails_when_salon_is_inactive(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
        salon
):

    salon.is_active = False
    salon.save()

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Appointment.objects.count() == 0





@pytest.mark.django_db
def test_reservation_fails_when_stylist_service_is_inactive(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
):

    stylist_service.is_active = False
    stylist_service.save()

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Appointment.objects.count() == 0


@pytest.mark.django_db
def test_reservation_fails_when_user_has_no_name_at_all(
        authenticated_client,
        appointment_date,
        stylist_service,
        appointment_time,
        working_hours,
        platform_settings,
        customer,
):

    customer.profile.first_name = ""
    customer.profile.last_name = ""
    customer.profile.save()

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
            "customer_name": ""
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert Appointment.objects.count() == 0
    assert response.data["error"] == "لطفا نام مشتری را وارد کنید."



@pytest.mark.django_db
def test_reservation_fails_when_slot_is_already_booked(
    authenticated_client,
    appointment_date,
    stylist_service,
    appointment_time,
    working_hours,
    platform_settings,
):
    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )

    Appointment.objects.create(
        start_time=start_datetime,
        end_time=start_datetime + timedelta(minutes=30),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="pending_payment",
    )

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Appointment.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_reservation_succeeds_when_previous_appointment_is_cancelled_by_customer(
    authenticated_client,
    appointment_date,
    stylist_service,
    appointment_time,
    working_hours,
    platform_settings,
):

    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )

    Appointment.objects.create(
        start_time=start_datetime,
        end_time=start_datetime + timedelta(minutes=30),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="cancelled_by_customer",
    )


    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Appointment.objects.count() == 2






@pytest.mark.django_db
def test_reservation_fails_when_appointment_is_cancelled_by_stylist(
    authenticated_client,
    appointment_date,
    stylist_service,
    appointment_time,
    working_hours,
    platform_settings,
):
    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )
    Appointment.objects.create(
        start_time=start_datetime,
        end_time=start_datetime + timedelta(minutes=30),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="cancelled_by_stylist",
    )

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Appointment.objects.count() == 1



@pytest.mark.django_db
def test_reservation_fails_when_given_datetime_is_past(
    authenticated_client,
    stylist_service,
):
    past_datetime = timezone.localtime() - timedelta(minutes=30)

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": past_datetime.date().isoformat(),
            "time": past_datetime.time().strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert Appointment.objects.count() == 0
    assert response.data["error"] == "امکان رزرو ساعت‌های گذشته وجود ندارد."



@pytest.mark.django_db(transaction=True)
def test_reservation_succeeds_when_previous_appointment_is_expired(
    authenticated_client,
    appointment_date,
    stylist_service,
    appointment_time,
    working_hours,
    platform_settings,
):

    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )
    previous_appointment = Appointment.objects.create(
        start_time=start_datetime,
        end_time=start_datetime + timedelta(minutes=30),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="expired",
    )

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert Appointment.objects.count() == 2
    assert response.data["appointment_id"] != previous_appointment.id


@pytest.mark.django_db
def test_expire_pending_appointment(
    stylist_service
):
    now = timezone.now()

    expired_appointment = Appointment.objects.create(
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, minutes=30),
        expires_at=now - timedelta(minutes=1),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="pending_payment",
    )

    valid_appointment = Appointment.objects.create(
        start_time=now + timedelta(days=2),
        end_time=now + timedelta(days=2, minutes=30),
        expires_at=now + timedelta(minutes=8),
        service_price_snapshot=500000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652588569",
        customer_name="hesam",
        status="pending_payment"
    )

    expire_pending_appointments()

    expired_appointment.refresh_from_db()
    valid_appointment.refresh_from_db()

    assert expired_appointment.status == "expired"
    assert valid_appointment.status == "pending_payment"





@pytest.mark.django_db
def test_confirmed_appointment_does_not_expire(
    stylist_service,
):

    now = timezone.now()

    appointment = Appointment.objects.create(
        start_time=now + timedelta(days=1),
        end_time=now + timedelta(days=1, minutes=30),
        expires_at=now - timedelta(minutes=1),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="confirmed",
    )

    expire_pending_appointments()

    appointment.refresh_from_db()

    assert appointment.status == "confirmed"



import threading

import pytest
from concurrent.futures import ThreadPoolExecutor
from django.db import close_old_connections
from rest_framework.test import APIClient
from django.urls import reverse


@pytest.mark.django_db(transaction=True)
def test_two_users_cannot_reserve_same_slot(
    customer,
    stylist_service,
    appointment_date,
    appointment_time,
    working_hours,
    platform_settings,
):
    another_customer = User.objects.create_user(
        phone_number="09123456789",
        password="test-password",
    )

    clients = []

    for user in (customer, another_customer):
        client = APIClient()
        client.force_authenticate(user=user)
        clients.append(client)

    data = {
        "date": appointment_date.isoformat(),
        "time": appointment_time.strftime("%H:%M"),
        "stylist_service": stylist_service.id,
    }

    barrier = threading.Barrier(2)

    def send_request(user):
        close_old_connections()

        try:
            client = APIClient()
            client.force_authenticate(user=user)

            barrier.wait()

            return client.post(
                reverse("appointment_create"),
                data=data,
                format="json",
            )
        finally:
            close_old_connections()

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_1 = executor.submit(send_request, customer)
        future_2 = executor.submit(send_request, another_customer)

        response_1 = future_1.result()
        response_2 = future_2.result()

    assert sorted([
        response_1.status_code,
        response_2.status_code,
    ]) == [201, 409]



@pytest.mark.django_db()
def test_users_cannot_reserve_overlapped_slots(
    customer,
    stylist_service,
    appointment_date,
    appointment_time,
    working_hours,
    platform_settings,
    authenticated_client
):
    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )

    Appointment.objects.create(
        start_time=start_datetime - timedelta(minutes=15),
        end_time=start_datetime + timedelta(minutes=15),
        expires_at=timezone.now() - timedelta(minutes=1),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="confirmed",
    )


    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert Appointment.objects.count() == 1
    assert response.status_code == 409



@pytest.mark.django_db(transaction=True)
def test_reserve_succeed_when_two_appointment_does_not_overlap(
    customer,
    stylist_service,
    appointment_date,
    appointment_time,
    working_hours,
    platform_settings,
    authenticated_client
):



    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )

    Appointment.objects.create(
        start_time=start_datetime + timedelta(minutes=30),
        end_time=start_datetime + timedelta(minutes=45),
        expires_at=timezone.now() - timedelta(minutes=1),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="confirmed",
    )

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service.id,
        }
    )

    assert response.status_code == 201
    assert Appointment.objects.count() == 2



@pytest.mark.django_db(transaction=True)
def test_different_stylists_can_have_same_time(
    customer,
    stylist_service,
    appointment_date,
    appointment_time,
    working_hours,
    platform_settings,
    authenticated_client,
    stylist_service2,
    working_hours2
):


    start_datetime = timezone.make_aware(
        datetime.combine(appointment_date, appointment_time)
    )

    Appointment.objects.create(
        start_time=start_datetime,
        end_time=start_datetime + timedelta(minutes=30),
        expires_at=timezone.now() - timedelta(minutes=1),
        service_price_snapshot=50000,
        deposit_amount=20000,
        platform_share=4000,
        salon_share=16000,
        stylist_service=stylist_service,
        customer_phone="09652584569",
        customer_name="hesam",
        status="confirmed",
    )

    response = authenticated_client.post(
        reverse("appointment_create"),
        data={
            "date": appointment_date.isoformat(),
            "time": appointment_time.strftime("%H:%M"),
            "stylist_service": stylist_service2.id,
        }
    )

    assert response.status_code == 201
    assert Appointment.objects.count() == 2
































