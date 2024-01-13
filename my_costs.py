from aiogram import Bot, Dispatcher, executor, types, filters
from data_base.requests_sql import DataBase
import datetime
import os
import emoji
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot)
id_users = []
users_id = {}

report_now = ['d', str(datetime.datetime.today().date()), 'day', 'день', 'сегодня', 'now', 'today']
report_month = ['m', str(datetime.datetime.today().date())[:7], 'month', 'месяц', 'за месяц']
report_year = ['Y', str(datetime.datetime.today().date())[:4], 'год', 'итог', 'итого', 'всего', 'all', 'year', 'за год',
               'сумма', 'все']
report_list = report_year + report_month + report_now
dict_name_month = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь'
}

kl = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
button_ = types.KeyboardButton(text='Сегодня')
button_1 = types.KeyboardButton(text='Месяц')
button_2 = types.KeyboardButton(text='Год')
button_3 = types.KeyboardButton(text=emoji.emojize(':pirate_flag:'))
button_4 = types.KeyboardButton(text='Удалить последнюю запись')

kl.add(button_, button_1, button_2, button_3, button_4)

inl_1 = types.InlineKeyboardButton('Да', callback_data='Yes')
inl_2 = types.InlineKeyboardButton('Нет', callback_data='No')
inline_kb = types.InlineKeyboardMarkup(row_width=2)
inline_kb.add(inl_1, inl_2)


def phrase(val='сегодня'):
    return '<b>Вы большой молодец!</b>' + emoji.emojize(":clapping_hands_medium-light_skin_tone:") + \
           f' Ничегошеньки за {val} не потратили! Так держать!!!' + \
           emoji.emojize(":smiling_face_with_sunglasses:")


async def get_data_month_or_day(message: types.Message, symbol: list):
    report, summa = DataBase().get_data(message.from_user.first_name, symbol[1])
    if report:
        if symbol[2] == 'day':
            await bot.send_message(message.chat.id, "<i>За {} вы потратили:</i>\n{}\n{}\n{}\nИтого: {} руб."
                                   .format(symbol[1], "-" * 30, report, "-" * 30, summa), parse_mode='html')
        else:
            await bot.send_message(message.chat.id,
                                   "<i>За {} месяц {} года вы потратили:</i>\n{}\n{}\n{}\nИтого: {} руб."
                                   .format(dict_name_month[int(symbol[1][5:])], symbol[1][:4], "-" * 30, report,
                                           "-" * 30, summa),
                                   parse_mode='html')
    else:
        await bot.send_message(message.chat.id, phrase(report_now[1]), parse_mode='html')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    name_id = message.from_user.first_name
    DataBase().start_data(name_id)
    if message.from_id not in id_users:
        id_users.append(message.from_id)
    await bot.send_message(message.chat.id,
                           f'Привет {message.from_user.first_name} я бот, который поможет тебе вести твой бюджет!'
                           f'\n\nЗаписывай сюда '
                           f'свои траты и контролируй свои расходы. \n\nНапример: "продукты 500" или "990 такси"... '
                           f'кавычки не нужны)))\n\n'
                           f'Ты сам выбираешь статьи своих расходов, и чтобы было проще считать, используй одинаковые '
                           f'категории: вместо "хлеб 500" или "молоко 100" - вноси: "продукты 500" и "продукты 100" '
                           f'соответственно... ну если только тебе не нужна подробнейшая статистика!!!'
                           f'\n\n'
                           f'{"*" * 40}'
                           f'{emoji.emojize(":pirate_flag:")} - УДАЛЯЕТ ВСЕ ЗАПИСИ, БУДЬ ВНИМАТЕЛЬНЕЕ!!!',
                           reply_markup=kl)


@dp.message_handler(lambda message: any(word in message.text.lower() for word in report_list))
async def send_report(message: types.Message):
    if message.text.lower() in report_now:
        await get_data_month_or_day(message, report_now)

    elif message.text.lower() in report_month:
        await get_data_month_or_day(message, report_month)

    elif message.text.lower() in report_year:
        dict_data_all = []
        all_price = 0
        for data in range(1, int(datetime.datetime.now().month) + 1):
            costs_for_month = str(datetime.date(int(report_year[1]), data, 1))[:7]
            report, summa = DataBase().get_data(message.from_user.first_name, costs_for_month)
            if report:
                dict_data_all.append(
                    f"\n{dict_name_month[data].upper()},{report},{'_' * 10},Итого: {summa} руб.,{'_' * 30},")
                all_price += summa
            else:
                dict_data_all.append(
                    f"\n{dict_name_month[data].upper()},Нет затрат!,{'_' * 30},")
        list_all_result = '\n'.join(['\n'.join(dict_data_all[i].split(',')) for i in range(len(dict_data_all))])
        await bot.send_message(message.chat.id,
                               f"{list_all_result}\n\n<em>За {datetime.datetime.now().year} год вы потратили: "
                               f"{all_price} руб.</em>", parse_mode='html')


@dp.message_handler(filters.Text(startswith='УДАЛИТЬ П', ignore_case=True))
async def del_last_record(message: types.Message):
    try:
        last_record = DataBase().del_data(message.from_user.first_name)
        await bot.send_message(message.chat.id, f'Запись <em>{last_record}</em> - удалена!', parse_mode='html')
    except Exception as ex:
        print(ex)
        await bot.send_message(message.chat.id, phrase(), parse_mode='html')


@dp.message_handler(filters.Text(equals=emoji.emojize(':pirate_flag:'), ignore_case=True))
async def del_all_data(message: types.Message):
    await bot.send_message(message.chat.id,
                           '<em>Вы точно хотите удалить все записи?</em>', parse_mode='html',
                           reply_markup=inline_kb)


@dp.callback_query_handler()
async def callback_query_del_all_data(callback: types.CallbackQuery):
    if f'{callback.from_user.id}' not in users_id:
        users_id[f'{callback.from_user.id}'] = callback.data
        await callback.answer(emoji.emojize(':OK_hand:'), show_alert=True)
        if callback.data == 'Yes':
            DataBase().del_data_all(callback.from_user.first_name)
            await bot.send_message(callback.message.chat.id,
                                   text=f'<em>ВСЕ ЗАПИСИ УДАЛЕНЫ!</em>\n{"*" * 30}', parse_mode='html')
            await callback.answer()

        else:
            await bot.send_message(callback.message.chat.id,
                                   text=f'<em>И правильно...удалим когда не сможем '
                                        f'сосчитать такие большие цифры))\n{"*" * 30}</em>', parse_mode='html')
            await callback.answer()
    else:
        await bot.send_message(callback.message.chat.id, f'{callback.from_user.first_name} ХВАТИТ опять '
                                                         f'ТЫКАТЬ НА КНОПКИ УЖЕ ФсЁ...')
        await bot.send_document(callback.message.chat.id,
                                document=open('/home/sssh/PycharmProjects/TelegrammBot/'
                                              'AcceptableFlamboyantAssassinbug-size_restricted.gif', 'rb'))
        await bot.edit_message_reply_markup(chat_id=callback.from_user.id,
                                            message_id=callback.message.message_id,
                                            reply_markup=None)
        await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
        del users_id[f'{callback.from_user.id}']


@dp.message_handler()
async def enter_expenditure(message: types.Message):
    try:
        answer = DataBase().insert_data(message.from_user.first_name, message.text.split()[0],
                                        message.text.split()[1], message.date)
        await bot.send_message(message.chat.id,
                               f'Сегодня Вы потратили на {answer[0].lower()}: {answer[1]} руб.')
    except Exception as ex:
        print(ex)
        await bot.send_message(message.chat.id,
                               'Введите правильно статью расходов!\n"Например: <em><u>продукты 500</u></em> \n'
                               'или <em><u>бензин 3000</u></em>"',
                               parse_mode='html')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
