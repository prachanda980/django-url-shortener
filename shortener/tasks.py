from celery import shared_task
from .models import ShortURL
from .utils import encode_base62
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import logging

logger = logging.getLogger('shortener')

@shared_task
def generate_short_key_task(url_id):
    logger.info(f"Starting async generation task for URL ID: {url_id}")
    try:
        url_obj = ShortURL.objects.get(id=url_id)
        # 1. Generate short key if needed
        if not url_obj.short_key and not url_obj.custom_key:
            url_obj.short_key = encode_base62(url_id + 100000)
            url_obj.status = 'done'
        elif url_obj.custom_key:
             url_obj.status = 'done'
        
        # 2. Generate QR Code
        import qrcode
        from io import BytesIO
        from django.core.files import File
        from django.conf import settings
        
        qr_data = f"{settings.SITE_URL}/{url_obj.short_key or url_obj.custom_key}/"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        file_name = f"qr_{url_obj.id}.png"
        url_obj.qr_code.save(file_name, File(buffer), save=False)
        
        url_obj.save()
        
        # Broadcast the new URL
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "url_updates",
            {
                "type": "url.update",
                "data": {
                    "action": "new_url",
                    "url_id": url_obj.id,
                    "original_url": url_obj.original_url,
                    "short_url": f"{settings.SITE_URL}/{url_obj.short_key or url_obj.custom_key}/",
                    "click_count": url_obj.click_count,
                    "status": url_obj.status,
                    "qr_code": url_obj.qr_code.url if url_obj.qr_code else None
                }
            }
        )
        
        logger.info(f"Successfully processed URL ID: {url_id}. Short key: {url_obj.short_key}")
    except ShortURL.DoesNotExist:
        logger.error(f"URL ID {url_id} not found in task.")
        pass
    except Exception as e:
        logger.error(f"Task failed for URL ID {url_id}: {str(e)}", exc_info=True)
        if 'url_obj' in locals():
            url_obj.status = 'failed'
            url_obj.save(update_fields=['status'])
