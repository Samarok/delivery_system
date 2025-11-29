HIGH_TEMPERATURE_THRESHOLD = 8.0
CRITICAL_TEMPERATURE_THRESHOLD = 10.0

DEFAULT_STATS_PERIOD_HOURS = 24
ALERT_LOOKBACK_PERIOD_HOURS = 24

DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

DELIVERY_STATUS_PENDING = "pending"
DELIVERY_STATUS_IN_TRANSIT = "in_transit"
DELIVERY_STATUS_DELIVERED = "delivered"
DELIVERY_STATUS_COMPLETED = "completed"

USER_ROLE_ADMIN = "admin"
USER_ROLE_DRIVER = "driver"
USER_ROLE_RECEIVER = "receiver"
USER_ROLE_DISPATCHER = "dispatcher"

ALERT_LEVEL_HIGH = "high"
ALERT_LEVEL_CRITICAL = "critical"
ALERT_LEVEL_NORMAL = "normal"

TEMPERATURE_TREND_RISING = "rising"
TEMPERATURE_TREND_FALLING = "falling"
TEMPERATURE_TREND_STABLE = "stable"

WS_MESSAGE_NEW_DATA = "new_data"
WS_MESSAGE_ALERT = "alert"
WS_MESSAGE_STATUS = "status"

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

MESSAGE_USER_CREATED = "Пользователь успешно создан"
MESSAGE_USER_UPDATED = "Пользователь успешно обновлен"
MESSAGE_USER_DELETED = "Пользователь успешно удален"
MESSAGE_ROLE_CREATED = "Роль успешно создана"
MESSAGE_DELIVERY_STATUS_UPDATED = "Статус доставки успешно обновлен"
MESSAGE_DELIVERY_CREATED = "Доставка успешно создана"
MESSAGE_DELIVERY_UPDATED = "Доставка успешно обновлена"
MESSAGE_SENSOR_DATA_CREATED = "Данные сенсора успешно сохранены"

ERROR_USER_NOT_FOUND = "Пользователь не найден"
ERROR_ROLE_NOT_FOUND = "Роль не найдена"
ERROR_DELIVERY_NOT_FOUND = "Доставка не найдена"
ERROR_SENSOR_DATA_NOT_FOUND = "Данные сенсора не найдены"
ERROR_INVALID_CREDENTIALS = "Неверное имя пользователя или пароль"
ERROR_INSUFFICIENT_PERMISSIONS = "Недостаточно прав"
ERROR_INVALID_TOKEN = "Недействительный токен"
ERROR_DELIVERY_STATUS_INVALID_TRANSITION = "Невозможно изменить статус доставки"
