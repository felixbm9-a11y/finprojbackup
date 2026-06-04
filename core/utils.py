import io
import random
import re

from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont

from users_app.constants import (AVATAR_COLORS, AVATAR_FONT_SIZE, AVATAR_SIZE,
                                 AVATAR_TEXT_COLOR)

PHONE_PREFIX = "+7"
PHONE_REPLACEMENT = "8"


def paginate_queryset(queryset, request, per_page, page_number=1):
    paginator = Paginator(queryset, per_page)
    page = request.GET.get("page", page_number)
    return paginator.get_page(page)

def build_avatar_image(first_letter: str) -> bytes:
    color = random.choice(AVATAR_COLORS)
    img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color)
    canvas = ImageDraw.Draw(img)

    letter = first_letter.upper()
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            size=AVATAR_FONT_SIZE,
        )
    except OSError:
        font = ImageFont.load_default()

    box = canvas.textbbox((0, 0), letter, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    pos_x = (AVATAR_SIZE - w) / 2 - box[0]
    pos_y = (AVATAR_SIZE - h) / 2 - box[1]
    canvas.text((pos_x, pos_y), letter, fill=AVATAR_TEXT_COLOR, font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def normalize_phone(raw: str) -> str:
    if raw.startswith(PHONE_PREFIX):
        return PHONE_REPLACEMENT + raw[2:]
    return raw