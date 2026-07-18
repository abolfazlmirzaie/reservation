# from datetime import date, time, timedelta, datetime
# from django.test import TestCase
# from django.utils import timezone as dj_timezone
# from django.contrib.auth import get_user_model
# from salon.models import Salon, Stylist, Service, StylistService, WorkingHours, DayOff
# from booking.models import Appointment
# from booking.services.booking_service import get_available_slots
#
# User = get_user_model()
#
#
# def make_aware_datetime(target_date, target_time):
#     naive_dt = datetime.combine(target_date, target_time)
#     return dj_timezone.make_aware(naive_dt)
#
#
# class GetAvailableSlotsTestCase(TestCase):
#     """
#     تست‌های سناریوهای مختلف برای تابع get_available_slots
#     """
#
#     def setUp(self):
#         """
#         این متد قبل از هر تست جداگانه اجرا میشه و داده‌های پایه رو می‌سازه.
#         هر تست، یه نسخه‌ی تازه و تمیز از این داده‌ها رو می‌گیره.
#         """
#         self.owner = User.objects.create_user(
#             username='testowner', password='testpass123'
#         )
#         self.salon = Salon.objects.create(
#             owner=self.owner,
#             name='سالن تست',
#             name_en='test salon',
#             category='womens_salon',
#             address='آدرس تست',
#             phone='09120000000',
#         )
#         self.stylist = Stylist.objects.create(
#             salon=self.salon,
#             name='آرایشگر تست',
#             name_en='test stylist',
#             booking_window_days=14,
#         )
#
#         for day in range(7):
#             WorkingHours.objects.create(
#                 stylist=self.stylist,
#                 day_of_week=day,
#                 start_time=time(9, 0),
#                 end_time=time(12, 0),
#                 is_active=True,
#             )
#
#         self.service_30min = Service.objects.create(
#             salon=self.salon, name='کوتاهی مو', is_active=True
#         )
#         self.stylist_service_30min = StylistService.objects.create(
#             stylist=self.stylist,
#             service=self.service_30min,
#             price=100000,
#             duration_minutes=30,
#         )
#
#         self.service_90min = Service.objects.create(
#             salon=self.salon, name='رنگ مو', is_active=True
#         )
#         self.stylist_service_90min = StylistService.objects.create(
#             stylist=self.stylist,
#             service=self.service_90min,
#             price=300000,
#             duration_minutes=90,
#         )
#
#         self.service_180min = Service.objects.create(
#             salon=self.salon, name='رنگ و مش کامل', is_active=True
#         )
#         self.stylist_service_180min = StylistService.objects.create(
#             stylist=self.stylist,
#             service=self.service_180min,
#             price=800000,
#             duration_minutes=180,
#         )
#
#         self.target_date = dj_timezone.localdate() + timedelta(days=1)
#
#     def _create_appointment(self, stylist_service, start_time, end_time, status='confirmed'):
#         return Appointment.objects.create(
#             stylist_service=stylist_service,
#             customer_name='مشتری تست',
#             customer_phone='09121111111',
#             start_time=make_aware_datetime(self.target_date, start_time),
#             end_time=make_aware_datetime(self.target_date, end_time),
#             status=status,
#             service_price_snapshot=stylist_service.price,
#             deposit_amount=20000,
#             platform_share=8000,
#             salon_share=12000,
#         )
#
#     # ==========================================
#     # سناریو ۱: روز کاملاً خالی
#     # ==========================================
#     def test_empty_day_returns_all_possible_slots(self):
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertIn(time(9, 0), slots)
#         self.assertIn(time(9, 30), slots)
#         self.assertIn(time(10, 0), slots)
#         self.assertIn(time(11, 30), slots)
#
#     # ==========================================
#     # سناریو ۲: یه نوبت وسط روز
#     # ==========================================
#     def test_single_appointment_blocks_overlapping_slots(self):
#         self._create_appointment(
#             self.stylist_service_30min, time(10, 0), time(10, 30)
#         )
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertNotIn(time(10, 0), slots)
#         self.assertIn(time(9, 30), slots)
#         self.assertIn(time(10, 30), slots)
#
#     # ==========================================
#     # سناریو ۳: نوبت طولانی باید اسلات‌های کوچیک‌تر داخلش رو هم مسدود کنه
#     # ==========================================
#     def test_long_appointment_blocks_all_overlapping_shorter_slots(self):
#         self._create_appointment(
#             self.stylist_service_90min, time(9, 0), time(10, 30)
#         )
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertNotIn(time(9, 0), slots)
#         self.assertNotIn(time(9, 30), slots)
#         self.assertNotIn(time(10, 0), slots)
#         self.assertIn(time(10, 30), slots)
#
#     # ==========================================
#     # سناریو ۴: خدمت طولانی باید از وسط شکاف خالی شروع بشه
#     # ==========================================
#     def test_long_service_finds_gap_after_existing_appointment(self):
#         WorkingHours.objects.filter(stylist=self.stylist).update(end_time=time(20, 0))
#
#         self._create_appointment(
#             self.stylist_service_90min, time(9, 0), time(10, 30)
#         )
#
#         slots = get_available_slots(self.stylist_service_180min, self.target_date)
#
#         self.assertIn(time(10, 30), slots)
#
#     # ==========================================
#     # سناریو ۵: شکاف کوچیک بین دو نوبت که کافی نیست
#     # ==========================================
#     def test_small_gap_between_appointments_not_offered_for_longer_service(self):
#         self._create_appointment(
#             self.stylist_service_30min, time(9, 0), time(9, 30)
#         )
#         self._create_appointment(
#             self.stylist_service_30min, time(9, 50), time(10, 20)
#         )
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertNotIn(time(9, 30), slots)
#
#     # ==========================================
#     # سناریو ۶: is_active=False
#     # ==========================================
#     def test_inactive_working_day_returns_no_slots(self):
#         day_of_week = self._get_model_day_of_week(self.target_date)
#         WorkingHours.objects.filter(
#             stylist=self.stylist, day_of_week=day_of_week
#         ).update(is_active=False)
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertEqual(slots, [])
#
#     # ==========================================
#     # سناریو ۷: DayOff
#     # ==========================================
#     def test_day_off_returns_no_slots(self):
#         DayOff.objects.create(stylist=self.stylist, date=self.target_date, reason='مرخصی تستی')
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertEqual(slots, [])
#
#     # ==========================================
#     # سناریو ۸: نوبت لغوشده نباید مسدودکننده باشه
#     # ==========================================
#     def test_cancelled_appointment_does_not_block_slot(self):
#         self._create_appointment(
#             self.stylist_service_30min, time(10, 0), time(10, 30),
#             status='cancelled_by_customer'
#         )
#
#         slots = get_available_slots(self.stylist_service_30min, self.target_date)
#
#         self.assertIn(time(10, 0), slots)
#
#     # ==========================================
#     # سناریو ۹: خارج از booking_window_days
#     # ==========================================
#     def test_date_beyond_booking_window_returns_no_slots(self):
#         self.stylist.booking_window_days = 3
#         self.stylist.save()
#
#         far_date = dj_timezone.localdate() + timedelta(days=10)
#
#         slots = get_available_slots(self.stylist_service_30min, far_date)
#
#         self.assertEqual(slots, [])
#
#     # ==========================================
#     # سناریو ۱۰: تاریخ گذشته
#     # ==========================================
#     def test_past_date_returns_no_slots(self):
#         past_date = dj_timezone.localdate() - timedelta(days=1)
#
#         slots = get_available_slots(self.stylist_service_30min, past_date)
#
#         self.assertEqual(slots, [])
#
#     # ==========================================
#     # متد کمکی داخلی
#     # ==========================================
#     def _get_model_day_of_week(self, target_date):
#         mapping = {5: 0, 6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6}
#         return mapping[target_date.weekday()]


from datetime import date, time, timedelta, datetime
from django.test import TestCase
from django.utils import timezone as dj_timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from salon.models import Salon, Stylist, Service, StylistService, WorkingHours
from booking.models import Appointment, PlatformSettings

User = get_user_model()


def make_aware_datetime(target_date, target_time):
    naive_dt = datetime.combine(target_date, target_time)
    return dj_timezone.make_aware(naive_dt)


class AppointmentCreateViewTestCase(APITestCase):
    """
    تست‌های سناریوهای مختلف برای endpoint ساخت نوبت (POST /appointment/)
    """

    def setUp(self):
        """
        داده‌های پایه‌ای که هر تست بهشون نیاز داره.
        این متد قبل از هر تست، جدا و از صفر اجرا میشه.
        """
        self.owner = User.objects.create_user(
            username='testowner', password='testpass123'
        )
        self.salon = Salon.objects.create(
            owner=self.owner,
            name='سالن تست',
            name_en='test salon',
            category='womens_salon',
            address='آدرس تست',
            phone='09120000000',
        )
        self.stylist = Stylist.objects.create(
            salon=self.salon,
            name='آرایشگر تست',
            name_en='test stylist',
            booking_window_days=14,
        )

        # ساعت کاری همه‌ی روزهای هفته: 09:00 تا 12:00
        for day in range(7):
            WorkingHours.objects.create(
                stylist=self.stylist,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_active=True,
            )

        self.service = Service.objects.create(
            salon=self.salon, name='کوتاهی مو', is_active=True
        )
        self.stylist_service = StylistService.objects.create(
            stylist=self.stylist,
            service=self.service,
            price=150000,
            duration_minutes=30,
        )

        # تنظیمات پلتفرم - این مدل باید حتماً یه رکورد داشته باشه وگرنه calculate_deposit خطا میده
        PlatformSettings.objects.create(
            deposit_percentage=15.00,
            deposit_minimum=20000,
            deposit_maximum=250000,
            platform_share_percentage=40.00,
        )

        self.target_date = dj_timezone.localdate() + timedelta(days=1)
        self.url = '/appointment/'  # مسیر واقعی endpoint خودت رو اینجا بذار اگه فرق داره

    def _valid_payload(self, target_time='10:00:00'):
        """
        یه دیکشنری آماده و معتبر برای ارسال به endpoint، که هر تست می‌تونه
        بخشی از اونو عوض کنه (مثلاً یه فیلد رو خالی بذاره برای تست خطا)
        """
        return {
            'stylist_service': self.stylist_service.id,
            'date': self.target_date.strftime('%Y-%m-%d'),
            'time': target_time,
            'customer_name': 'مریم احمدی',
            'customer_number': '09121111111',
        }

    # ==========================================
    # سناریو ۱: رزرو موفق با داده‌ی کاملاً معتبر
    # ==========================================
    def test_successful_booking_creates_appointment(self):
        """
        وقتی همه‌ی داده‌ها معتبرن و ساعت واقعاً خالیه، باید نوبت با موفقیت ساخته بشه
        """
        response = self.client.post(self.url, self._valid_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('appointment_id', response.data)
        self.assertIn('deposit_amount', response.data)

        # مطمئن شو واقعاً یه رکورد تو دیتابیس ساخته شده
        self.assertEqual(Appointment.objects.count(), 1)

    # ==========================================
    # سناریو ۲: محاسبه‌ی مالی درست انجام شده باشه
    # ==========================================
    def test_successful_booking_calculates_correct_financials(self):
        """
        بررسی می‌کنه که مبلغ بیعانه و سهم‌ها طبق تنظیمات PlatformSettings درست حساب شدن
        """
        response = self.client.post(self.url, self._valid_payload(), format='json')

        appointment = Appointment.objects.get(id=response.data['appointment_id'])

        # قیمت خدمت 150000 با 15% بیعانه = 22500 (بین حداقل 20000 و حداکثر 250000 هست، پس دست‌نخورده می‌مونه)
        self.assertEqual(appointment.service_price_snapshot, 150000)
        self.assertEqual(appointment.deposit_amount, 22500)
        self.assertEqual(appointment.platform_share, 9000)  # 40% از 22500
        self.assertEqual(appointment.salon_share, 13500)  # 60% از 22500

    # ==========================================
    # سناریو ۳: وضعیت اولیه‌ی نوبت باید pending_payment باشه
    # ==========================================
    def test_new_appointment_status_is_pending_payment(self):
        """
        نوبت تازه‌ساخته‌شده نباید مستقیم confirmed باشه، چون هنوز پرداخت انجام نشده
        """
        response = self.client.post(self.url, self._valid_payload(), format='json')

        appointment = Appointment.objects.get(id=response.data['appointment_id'])
        self.assertEqual(appointment.status, 'pending_payment')

    # ==========================================
    # سناریو ۴: تلاش برای رزرو یه ساعت از قبل اشغال‌شده (Race Condition)
    # این مهم‌ترین تسته - دقیقاً همون منطق محافظتی که با هم طراحی کردیم
    # ==========================================
    def test_booking_already_taken_slot_returns_conflict(self):
        """
        اگه یه نوبت از قبل دقیقاً همون ساعت رو گرفته باشه، درخواست دوم باید رد بشه
        """
        # اول یه نوبت موفق برای ساعت 10:00 می‌سازیم
        first_response = self.client.post(self.url, self._valid_payload(target_time='10:00:00'), format='json')
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        # حالا دوباره سعی می‌کنیم دقیقاً همون ساعت رو بگیریم
        second_response = self.client.post(self.url, self._valid_payload(target_time='10:00:00'), format='json')

        self.assertEqual(second_response.status_code, status.HTTP_409_CONFLICT)
        self.assertIn('error', second_response.data)

        # مطمئن شو فقط یه نوبت ساخته شده، نه دوتا
        self.assertEqual(Appointment.objects.count(), 1)

    # ==========================================
    # سناریو ۵: نوبت لغوشده نباید مانع رزرو مجدد همون ساعت بشه
    # ==========================================
    def test_can_rebook_slot_after_previous_appointment_cancelled(self):
        """
        اگه نوبت قبلی لغو بشه، باید بشه دوباره همون ساعت رو رزرو کرد
        """
        first_response = self.client.post(self.url, self._valid_payload(target_time='10:00:00'), format='json')
        appointment = Appointment.objects.get(id=first_response.data['appointment_id'])
        appointment.status = 'cancelled_by_customer'
        appointment.save()

        second_response = self.client.post(self.url, self._valid_payload(target_time='10:00:00'), format='json')

        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)

    # ==========================================
    # سناریو ۶: فیلد الزامی خالی باشه (مثلاً customer_name)
    # ==========================================
    def test_missing_required_field_returns_bad_request(self):
        """
        اگه یکی از فیلدهای الزامی (مثل customer_name) نباشه، باید خطای 400 بگیریم،
        نه اینکه سیستم crash کنه
        """
        payload = self._valid_payload()
        del payload['customer_name']

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Appointment.objects.count(), 0)

    # ==========================================
    # سناریو ۷: stylist_service با id نامعتبر (وجود نداره)
    # ==========================================
    def test_invalid_stylist_service_id_returns_bad_request(self):
        """
        اگه id ای که فرستاده میشه اصلاً تو دیتابیس نباشه، باید خطای مناسب بگیریم
        """
        payload = self._valid_payload()
        payload['stylist_service'] = 9999  # idای که وجود نداره

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==========================================
    # سناریو ۸: فرمت تاریخ نامعتبر
    # ==========================================
    def test_invalid_date_format_returns_bad_request(self):
        """
        اگه تاریخ با فرمت اشتباه فرستاده بشه (مثلاً به‌جای YYYY-MM-DD یه چیز دیگه)،
        نباید سیستم crash کنه
        """
        payload = self._valid_payload()
        payload['date'] = '20-07-2026'  # فرمت اشتباه

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)