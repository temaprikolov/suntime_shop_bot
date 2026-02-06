import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router as user_router
from admin import router as admin_router
from database import init_db
import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    print("🚀 Запуск бота SunShop...")
    print("🔄 Инициализация базы данных...")
    
    try:
        init_db()
        print("✅ База данных инициализирована (8 товаров)")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return
    
    bot = Bot(
        token=config.config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    print("✅ Бот инициализирован")
    bot_info = await bot.get_me()
    print(f"🤖 Имя бота: @{bot_info.username}")
    print(f"👑 Админы: {config.config.ADMINS}")
    print(f"📢 Канал: {config.config.CHANNEL_ID}")
    
    try:
        bot_member = await bot.get_chat_member(
            chat_id=config.config.CHANNEL_ID,
            user_id=bot_info.id
        )
        if bot_member.status in ['administrator', 'creator']:
            print("✅ Бот является администратором канала")
        else:
            print("⚠️ ВНИМАНИЕ: Бот НЕ является администратором канала!")
            print("Бот не сможет проверять подписки пользователей.")
            print(f"Добавьте бота @{bot_info.username} как администратора в канал @SUNTIMENEWS")
    except Exception as e:
        print(f"⚠️ Ошибка при проверке прав бота: {e}")
        print("Убедитесь, что бот добавлен в канал!")
    
    print("📋 Меню содержит 8 кнопок:")
    print("  1. 🔥 РАСПРОДАЖА (ID 7)")
    print("  2. 🎲 РАНДОМНЫЙ ТОВАР (ID 8)")
    print("  3. НАЛИЧИЕ ЖИДКОСТИ (ID 1)")
    print("  4. НАЛИЧИЕ СН*СА И ПЛАСТИНОК (ID 2)")
    print("  5. НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС (ID 3)")
    print("  6. НАЛИЧИЕ РАСХОДНИКОВ (ID 4)")
    print("  7. НАЛИЧИЕ POD-УСТРОЙСТВ (ID 5)")
    print("  8. ИНФОРМАЦИЯ О ЗАВОЗЕ (ID 6)")
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    print("\n🔄 Бот запущен и ожидает сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not config.config.BOT_TOKEN:
        print("❌ ОШИБКА: Не указан токен бота!")
        print(f"Текущий токен: {config.config.BOT_TOKEN}")
        sys.exit(1)
    
    os.makedirs("data", exist_ok=True)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        logger.exception("Ошибка при запуске бота:")
