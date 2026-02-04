from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Session, User, Product
import config
import csv
import io
import os
import sys
import subprocess
from datetime import datetime

router = Router()

print("✅ Модуль admin.py загружен")

class AdminStates(StatesGroup):
    waiting_for_broadcast = State()
    waiting_for_new_text = State()
    waiting_for_username = State()
    waiting_for_user_message = State()

def admin_menu_kb():
    keyboard = [
        [InlineKeyboardButton(text="✏️ Редактировать текст товаров", callback_data="edit_texts")],
        [InlineKeyboardButton(text="📢 Сделать рассылку", callback_data="broadcast")],
        [InlineKeyboardButton(text="✉️ Отправить сообщение пользователю", callback_data="send_to_user")],
        [InlineKeyboardButton(text="🔄 Перезапустить бота", callback_data="restart_bot")],
        [InlineKeyboardButton(text="📊 Получить базу данных", callback_data="get_db")],
        [InlineKeyboardButton(text="⬅️ Выйти из админки", callback_data="exit_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def edit_texts_kb():
    keyboard = [
        [InlineKeyboardButton(text="🔥 РАСПРОДАЖА", callback_data="edit_7")],
        [InlineKeyboardButton(text="🎲 РАНДОМНЫЙ ТОВАР", callback_data="edit_8")],
        [InlineKeyboardButton(text="НАЛИЧИЕ ЖИДКОСТЕЙ", callback_data="edit_1")],
        [InlineKeyboardButton(text="НАЛИЧИЕ СН*СА И ПЛАСТИНОК", callback_data="edit_2")],
        [InlineKeyboardButton(text="НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС", callback_data="edit_3")],
        [InlineKeyboardButton(text="НАЛИЧИЕ РАСХОДНИКОВ", callback_data="edit_4")],
        [InlineKeyboardButton(text="НАЛИЧИЕ POD-УСТРОЙСТВ", callback_data="edit_5")],
        [InlineKeyboardButton(text="ИНФОРМАЦИЯ О ЗАВОЗЕ", callback_data="edit_6")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def restart_menu_kb():
    keyboard = [
        [InlineKeyboardButton(text="♻️ Перезапустить бота", callback_data="restart_execute")],
        [InlineKeyboardButton(text="📊 Проверить состояние бота", callback_data="check_bot_status")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def is_admin(user_id: int) -> bool:
    return user_id in config.config.ADMINS

@router.message(Command("admin"))
async def admin_panel(message: Message):
    print(f"👑 Запрос админ панели от пользователя {message.from_user.id}")
    
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа к админ панели")
        return
    
    await message.answer(
        "👑 <b>Админ панель SUNTIME SHOP</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_menu_kb(),
    )

@router.callback_query(F.data == "admin_menu")
async def admin_menu_callback(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.message.edit_text(
        "👑 <b>Админ панель SUNTIME SHOP</b>\n\n"
        "Выберите действие:",
        reply_markup=admin_menu_kb(),
    )

@router.callback_query(F.data == "restart_bot")
async def restart_bot_menu(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.message.edit_text(
        "🔄 <b>Управление перезапуском бота</b>\n\n"
        "Выберите действие:",
        reply_markup=restart_menu_kb(),
    )

@router.callback_query(F.data == "check_bot_status")
async def check_bot_status(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    try:
        bot_info = await callback.bot.get_me()
        
        session = Session()
        users_count = session.query(User).count()
        products_count = session.query(Product).count()
        session.close()
        
        db_size = 0
        if os.path.exists('data/database.db'):
            db_size = os.path.getsize('data/database.db') / 1024
        
        status_text = (
            "📊 <b>Статус бота:</b>\n\n"
            f"🤖 Имя бота: @{bot_info.username}\n"
            f"🆔 ID бота: {bot_info.id}\n"
            f"✅ Статус: 🟢 Активен\n\n"
            f"📊 <b>База данных:</b>\n"
            f"👥 Пользователей: {users_count}\n"
            f"📦 Товаров: {products_count}\n"
            f"💾 Размер БД: {db_size:.1f} KB\n\n"
            f"🕒 Последняя проверка: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        await callback.message.edit_text(
            status_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Перезапустить бота", callback_data="restart_execute")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="restart_bot")]
            ]),
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ <b>Ошибка при проверке статуса:</b>\n\n{str(e)}\n\n"
            "Бот может быть недоступен. Попробуйте перезапустить.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Срочный перезапуск", callback_data="restart_execute")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="restart_bot")]
            ]),
        )

@router.callback_query(F.data == "restart_execute")
async def restart_execute(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.message.edit_text(
        "🔄 <b>Перезапуск бота...</b>\n\n"
        "Пожалуйста, подождите 10-20 секунд.",
    )
    
    try:
        await callback.bot.session.close()
        
        with open('restart.trigger', 'w') as f:
            f.write(str(datetime.now()))
        
        await callback.message.edit_text(
            "✅ <b>Команда перезапуска отправлена!</b>\n\n"
            "Бот попытается перезапуститься автоматически.\n"
            "Если он не перезапустится через 30 секунд,\n"
            "перезапустите его вручную командой:\n"
            "<code>python main.py</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Проверить статус", callback_data="check_bot_status")],
                [InlineKeyboardButton(text="⬅️ В админку", callback_data="admin_menu")]
            ]),
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ <b>Ошибка при перезапуске:</b>\n\n{str(e)}\n\n"
            "Попробуйте перезапустить бота вручную.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="restart_execute")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="restart_bot")]
            ]),
        )

@router.callback_query(F.data == "edit_texts")
async def edit_texts(callback: CallbackQuery):
    """Редактирование текстов"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    session = Session()
    products = session.query(Product).order_by(Product.id).all()
    
    text = "📝 <b>Текущие тексты:</b>\n\n"
    for product in products:
        preview = product.item_text[:50] + "..." if len(product.item_text) > 50 else product.item_text
        text += f"<b>{product.item_name}:</b>\n{preview}\n\n"
    
    text += "Выберите текст для редактирования:"
    
    session.close()
    
    await callback.message.edit_text(
        text,
        reply_markup=edit_texts_kb(),
    )

@router.callback_query(F.data.startswith("edit_"))
async def select_text_to_edit(callback: CallbackQuery, state: FSMContext):
    """Выбор текста для редактирования"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    item_id = int(callback.data.split("_")[1])
    
    session = Session()
    product = session.query(Product).filter_by(id=item_id).first()
    
    if not product:
        # Если товара нет, создаем его
        product_names = {
            1: "НАЛИЧИЕ ЖИДКОСТЕЙ",
            2: "НАЛИЧИЕ СН*СА И ПЛАСТИНОК",
            3: "НАЛИЧИЕ ОДНОРАЗОВЫХ ОЭС",
            4: "НАЛИЧИЕ РАСХОДНИКОВ",
            5: "НАЛИЧИЕ POD-УСТРОЙСТВ",
            6: "ИНФОРМАЦИЯ О ЗАВОЗЕ",
            7: "🔥 РАСПРОДАЖА",
            8: "🎲 РАНДОМНЫЙ ТОВАР"
        }
        product = Product(
            id=item_id,
            item_name=product_names.get(item_id, f"Товар {item_id}"),
            item_text=""
        )
        session.add(product)
        session.commit()
    
    await state.update_data(item_id=item_id, product_name=product.item_name)
    
    await callback.message.edit_text(
        f"✏️ <b>Редактирование: {product.item_name}</b>\n\n"
        f"Текущий текст:\n{product.item_text}\n\n"
        "Отправьте новый текст:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="edit_texts")]
        ]),
    )
    
    await state.set_state(AdminStates.waiting_for_new_text)
    session.close()

@router.message(AdminStates.waiting_for_new_text)
async def save_new_text(message: Message, state: FSMContext):
    """Сохранение нового текста"""
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        await state.clear()
        return
    
    data = await state.get_data()
    item_id = data.get('item_id')
    product_name = data.get('product_name')
    
    if not item_id:
        await message.answer("❌ Ошибка. Попробуйте снова.")
        await state.clear()
        return
    
    session = Session()
    product = session.query(Product).filter_by(id=item_id).first()
    
    if product:
        product.item_text = message.text
        session.commit()
        
        await message.answer(
            f"✅ Текст для <b>{product_name}</b> успешно обновлен!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад к редактированию", callback_data="edit_texts")]
            ]),
        )
    else:
        await message.answer("❌ Товар не найден")
    
    session.close()
    await state.clear()

@router.callback_query(F.data == "broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    """Начало рассылки"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.message.edit_text(
        "📢 <b>Рассылка сообщения</b>\n\n"
        "Отправьте сообщение для рассылки всем пользователям:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_menu")]
        ]),
    )
    
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def process_broadcast(message: Message, state: FSMContext):
    """Обработка рассылки"""
    if not await is_admin(message.from_user.id):
        await state.clear()
        return
    
    await message.answer("⏳ Начинаю рассылку...")
    
    session = Session()
    users = session.query(User).all()
    session.close()
    
    success = 0
    failed = 0
    
    for user in users:
        try:
            await message.copy_to(chat_id=user.user_id, reply_markup=message.reply_markup)
            success += 1
        except:
            failed += 1
        
        import asyncio
        await asyncio.sleep(0.05)
    
    await message.answer(
        f"📊 <b>Рассылка завершена:</b>\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Не удалось: {failed}\n\n"
        f"Всего пользователей: {success + failed}",
        reply_markup=admin_menu_kb(),
    )
    
    await state.clear()

@router.callback_query(F.data == "get_db")
async def get_database(callback: CallbackQuery):
    """Получение базы данных пользователей"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    session = Session()
    users = session.query(User).all()
    session.close()
    
    if not users:
        await callback.answer("📭 База данных пуста")
        return
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['ID', 'User ID', 'Username', 'First Name', 'Last Name', 'Joined At', 'Is Admin'])
    
    for user in users:
        writer.writerow([
            user.id,
            user.user_id,
            user.username or '',
            user.first_name or '',
            user.last_name or '',
            user.joined_at.strftime('%Y-%m-%d %H:%M:%S'),
            'Да' if user.is_admin else 'Нет'
        ])
    
    output.seek(0)
    
    text_file = io.BytesIO(output.getvalue().encode('utf-8'))
    text_file.name = f'users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    await callback.bot.send_document(
        chat_id=callback.from_user.id,
        document=text_file,
        caption=f"📊 База данных пользователей\n👥 Всего: {len(users)} пользователей"
    )
    
    await callback.answer("✅ База данных отправлена в личные сообщения")

@router.callback_query(F.data == "exit_admin")
async def exit_admin(callback: CallbackQuery):
    """Выход из админки"""
    from handlers import main_menu_kb
    
    await callback.message.edit_text(
        "🏪 <b>НАЛИЧИЕ ТОВАРА SUNTIME</b>\n\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb(),
    )

# ОТПРАВКА СООБЩЕНИЙ ПОЛЬЗОВАТЕЛЯМ

@router.callback_query(F.data == "send_to_user")
async def send_to_user_start(callback: CallbackQuery, state: FSMContext):
    """Начало отправки сообщения пользователю"""
    if not await is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа")
        return
    
    await callback.message.edit_text(
        "✉️ <b>Отправка сообщения пользователю</b>\n\n"
        "Введите username пользователя (с @ или без):\n\n"
        "<i>Примеры:\n• username123\n• @username123\n• user (поиск по части username)</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_menu")]
        ]),
    )
    
    await state.set_state(AdminStates.waiting_for_username)

@router.message(AdminStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    """Обработка username"""
    if not await is_admin(message.from_user.id):
        await state.clear()
        return
    
    username = message.text.strip()
    
    # Убираем @ если он есть в начале
    if username.startswith('@'):
        username = username[1:]
    
    if not username:
        await message.answer(
            "❌ Вы не ввели username!\n\n"
            "Введите username пользователя (с @ или без):",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_menu")]
            ]),
        )
        return
    
    # Ищем пользователя в БД
    session = Session()
    
    # Ищем сначала точное совпадение
    user = session.query(User).filter(User.username.ilike(username)).first()
    
    # Если не нашли точное совпадение, ищем частичное
    if not user:
        user = session.query(User).filter(User.username.ilike(f"%{username}%")).first()
    
    session.close()
    
    if not user:
        await message.answer(
            f"❌ Пользователь с username '{username}' не найден в базе.\n\n"
            "Попробуйте снова или введите другой username:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_menu")]
            ]),
        )
        return
    
    await state.update_data(
        target_user_id=user.user_id,
        target_username=user.username,
        target_first_name=user.first_name
    )
    
    await message.answer(
        f"✅ Найден пользователь:\n\n"
        f"👤 ID: {user.user_id}\n"
        f"📛 Username: @{user.username}\n"
        f"👤 Имя: {user.first_name}\n\n"
        f"Теперь отправьте сообщение для этого пользователя:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Отмена", callback_data="admin_menu")]
        ]),
    )
    
    await state.set_state(AdminStates.waiting_for_user_message)

@router.message(AdminStates.waiting_for_user_message)
async def send_user_message(message: Message, state: FSMContext):
    """Отправка сообщения пользователю"""
    if not await is_admin(message.from_user.id):
        await state.clear()
        return
    
    data = await state.get_data()
    target_user_id = data.get('target_user_id')
    target_username = data.get('target_username')
    
    if not target_user_id:
        await message.answer("❌ Ошибка: пользователь не найден")
        await state.clear()
        return
    
    try:
        # Отправляем сообщение пользователю
        await message.copy_to(
            chat_id=target_user_id,
            caption=f"📨 <b>Сообщение от администратора магазина:</b>\n\n{message.caption or ''}"
        )
        
        await message.answer(
            f"✅ Сообщение успешно отправлено пользователю:\n\n"
            f"👤 ID: {target_user_id}\n"
            f"📛 Username: @{target_username}\n\n"
            f"<i>Вы можете отправить еще одно сообщение или вернуться в меню</i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📨 Отправить еще", callback_data="send_to_user")],
                [InlineKeyboardButton(text="⬅️ В админку", callback_data="admin_menu")]
            ]),
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить сообщение:\n\n{str(e)}\n\n"
            f"Возможно, пользователь заблокировал бота.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ В админку", callback_data="admin_menu")]
            ]),
        )
    
    await state.clear()

# КОМАНДА ПОИСКА ПОЛЬЗОВАТЕЛЯ

@router.message(Command("find"))
async def find_user(message: Message):
    """Поиск пользователя по username или ID"""
    if not await is_admin(message.from_user.id):
        await message.answer("⛔ Нет доступа")
        return
    
    if len(message.text.split()) < 2:
        await message.answer(
            "🔍 <b>Поиск пользователя</b>\n\n"
            "Использование:\n"
            "/find username - поиск по username\n"
            "/find @username - поиск по username\n"
            "/find 12345678 - поиск по ID"
        )
        return
    
    search_term = message.text.split(maxsplit=1)[1].strip()
    
    session = Session()
    
    # Проверяем, не ID ли это (число)
    if search_term.isdigit():
        user_id = int(search_term)
        user = session.query(User).filter_by(user_id=user_id).first()
        search_type = "ID"
    else:
        # Убираем @ если есть
        if search_term.startswith('@'):
            search_term = search_term[1:]
        
        # Ищем по username
        user = session.query(User).filter(User.username.ilike(f"%{search_term}%")).first()
        search_type = "username"
    
    if not user:
        await message.answer(f"❌ Пользователь с {search_type} '{search_term}' не найден.")
        session.close()
        return
    
    await message.answer(
        f"🔍 <b>Найден пользователь:</b>\n\n"
        f"👤 ID: {user.user_id}\n"
        f"📛 Username: @{user.username}\n"
        f"👤 Имя: {user.first_name}\n"
        f"👤 Фамилия: {user.last_name or 'Не указана'}\n"
        f"📅 Дата регистрации: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"👑 Админ: {'Да' if user.is_admin else 'Нет'}\n\n"
        f"✉️ <a href='tg://user?id={user.user_id}'>Написать пользователю</a>"
    )
    
    session.close()
