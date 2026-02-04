from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart, Command
from database import Session, User, Product
import config

router = Router()

print("✅ Модуль handlers.py загружен")

def check_subscription_kb():
    """Клавиатура для проверки подписки"""
    keyboard = [
        [InlineKeyboardButton(text="📢 Подписаться на канал", url="https://t.me/SUNTIMENEWS")],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def check_user_subscription(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=config.config.CHANNEL_ID,
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"❌ Ошибка при проверке подписки: {e}")
        return False

def main_menu_kb():
    keyboard = [
        [InlineKeyboardButton(text="🔥 РАСПРОДАЖА", callback_data="item_7")],
        [InlineKeyboardButton(text="🎲 РАНДОМНЫЙ ТОВАР", callback_data="item_8")],
        [InlineKeyboardButton(text="НАЛИЧИЕ ЖИДКОСТИ", callback_data="item_1")],
        [InlineKeyboardButton(text="НАЛИЧИЕ СН*СА И ПЛАСТИНОК", callback_data="item_2")],
        [InlineKeyboardButton(text="НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС", callback_data="item_3")],
        [InlineKeyboardButton(text="НАЛИЧИЕ РАСХОДНИКОВ", callback_data="item_4")],
        [InlineKeyboardButton(text="НАЛИЧИЕ POD-УСТРОЙСТВ", callback_data="item_5")],
        [InlineKeyboardButton(text="ИНФОРМАЦИЯ О ЗАВОЗЕ", callback_data="item_6")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def back_to_menu_kb():
    keyboard = [
        [InlineKeyboardButton(text="Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"👤 Пользователь {message.from_user.id} запустил бота")
    
    subscribed = await check_user_subscription(message.from_user.id, message.bot)
    
    if not subscribed:
        await message.answer(
            "👋 Привет! Добро пожаловать в <b>SUNTIME SHOP</b>!\n\n"
            "Для доступа к магазину необходимо подписаться на наш канал:",
            reply_markup=check_subscription_kb(),
        )
        return
    
    session = Session()
    user = session.query(User).filter_by(user_id=message.from_user.id).first()
    if not user:
        user = User(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            is_admin=message.from_user.id in config.config.ADMINS
        )
        session.add(user)
    else:
        user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
    
    session.commit()
    session.close()
    
    await message.answer(
        "🏪 <b>НАЛИЧИЕ ТОВАРА SUNTIME</b>\n\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb(),
    )

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    """Проверка подписки"""
    subscribed = await check_user_subscription(callback.from_user.id, callback.bot)
    
    if subscribed:
        session = Session()
        user = session.query(User).filter_by(user_id=callback.from_user.id).first()
        if not user:
            user = User(
                user_id=callback.from_user.id,
                username=callback.from_user.username,
                first_name=callback.from_user.first_name,
                last_name=callback.from_user.last_name,
                is_admin=callback.from_user.id in config.config.ADMINS
            )
            session.add(user)
            session.commit()
        session.close()
        
        await callback.message.edit_text(
            "🏪 <b>НАЛИЧИЕ ТОВАРА SUNTIME</b>\n\n"
            "Выберите категорию:",
            reply_markup=main_menu_kb(),
        )
    else:
        await callback.answer("❌ Вы не подписаны на канал!", show_alert=True)

@router.callback_query(F.data.startswith("item_"))
async def show_item(callback: CallbackQuery):
    item_id = callback.data.split("_")[1]
    
    session = Session()
    try:
        item_num = int(item_id)
        product = session.query(Product).filter_by(id=item_num).first()
    except:
        product = None
    
    if product:
        text = product.item_text
        display_name = product.item_name
    else:
        texts = {
            7: config.config.ITEM_SALE_TEXT,
            8: config.config.ITEM_RANDOM_TEXT,
            1: config.config.ITEM1_TEXT,
            2: config.config.ITEM2_TEXT,
            3: config.config.ITEM3_TEXT,
            4: config.config.ITEM4_TEXT,
            5: config.config.ITEM5_TEXT,
            6: config.config.INFO_TEXT
        }
        
        item_names = {
            7: "🔥 РАСПРОДАЖА",
            8: "🎲 РАНДОМНЫЙ ТОВАР",
            1: "НАЛИЧИЕ ЖИДКОСТЕЙ",
            2: "НАЛИЧИЕ СН*СА И ПЛАСТИНОК", 
            3: "НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС",
            4: "НАЛИЧИЕ РАСХОДНИКОВ",
            5: "НАЛИЧИЕ POD-УСТРОЙСТВ",
            6: "ИНФОРМАЦИЯ О ЗАВОЗЕ"
        }
        
        text = texts.get(int(item_id), "Информация обновляется...")
        display_name = item_names.get(int(item_id), "Товар")
    
    session.close()
    
    await callback.message.edit_text(
        f"<b>{display_name}</b>\n\n{text}",
        reply_markup=back_to_menu_kb(),
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "🏪 <b>НАЛИЧИЕ ТОВАРА SUNTIME</b>\n\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb(),
    )

@router.message(Command("menu"))
async def show_menu(message: Message):
    """Команда для показа меню"""
    await message.answer(
        "🏪 <b>НАЛИЧИЕ ТОВАРА SUNTIME</b>\n\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb(),
    )

@router.message(Command("myid"))
async def get_my_id(message: Message):
    """Получить свой ID"""
    await message.answer(f"👤 Ваш ID: {message.from_user.id}\n"
                        f"📛 Username: @{message.from_user.username}\n"
                        f"👥 Админы в конфиге: {config.config.ADMINS}")
