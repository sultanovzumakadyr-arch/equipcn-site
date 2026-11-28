# LazerTruba — лазерные станки для резки труб

Сайт: https://equipcngroup.com/lazertruba/ (временно на домене Equipcn; для своего домена поменять SITE в build.py и перенести site/lazertruba в отдельный репозиторий).

- build.py — все данные: 6 серий, комплектации, цены завода в юанях, фото, видео, тексты. Запуск: python lazertruba/build.py
- Цена = юани / 6,68 + наценка в $ (до 45 000 юаней +800, 45–62 тыс. +900, MYS +1500, YQ +2000) x 458,28 тенге, вверх до 10 000. Без доставки в Казахстан и растаможки.
- Фото: site/lazertruba/media/p, видео: site/lazertruba/media/v (720p, без звука).
- Заявки: тот же приём заявок, что на equipcngroup.com (lazertruba/tracking.json, поле lead_endpoint).
