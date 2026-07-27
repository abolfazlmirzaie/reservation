from booking.models import PlatformSettings



def calculate_deposit(stylist_service):

    settings = PlatformSettings.objects.first()
    price = stylist_service.price

    deposit = price * settings.deposit_percentage / 100
    deposit = max(settings.deposit_minimum, min(deposit, settings.deposit_maximum))

    platform_share = int(deposit * settings.platform_share_percentage / 100)
    salon_share = int(deposit) - platform_share

    return {
        'service_price_snapshot': price,
        'deposit_amount': int(deposit),
        'platform_share': platform_share,
        'salon_share': salon_share,
    }
