#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import remove as rm_file
from telebot import TeleBot, types  # pip3 install pyTelegramBotAPI
from JsonBase import JsonBase

DATABASE = JsonBase('database.json')

data = {
    'token': '...TOKEN...',  # telegram bot token => https://t.me/BotFather
    'admin': [1879234583],  # your numberic id => https://t.me/userinfobot
    'channel': '...channel_username...'  # without @
}

bot = TeleBot(data['token'])

def addUser(db: JsonBase, user_id):
  data_db = db.get()
  if ((type(data_db).__name__ == 'dict') == False):
    data_db = dict()
    data_db['users_id'], data_db['users_data'] = [], {}
    db.commit(data_db)

  data_db = db.get()
  if user_id not in data_db['users_id']:
    data_db['users_id'].append(user_id)

    data_db['users_data']["%s" % user_id] = {}

    data_db['users_data']["%s" % user_id]['status'] = None
    data_db['users_data']["%s" % user_id]['ads'] = {}
    data_db['users_data']["%s" % user_id]['tmp'] = {}
    data_db['users_data']["%s" % user_id]['block'] = False

    db.commit(data_db)

  return True

def start_btn(user_id):
    start_btn = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    bs1 = types.KeyboardButton('مدیریت آگهی ها 🗂')
    bs2 = types.KeyboardButton('ثبت آگهی جدید 📇')
    bs3 = types.KeyboardButton('راهنما 📕')
    bs4 = types.KeyboardButton('پنل ادمین 🖥')
    
    start_btn.add(bs1, bs2, bs3)
    
    if user_id in data['admin']:
        start_btn.add(bs4)

    return start_btn

cancel_btn = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
cb = types.KeyboardButton('انصراف')
cancel_btn.add(cb)

back_admin = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
ba = types.KeyboardButton('بازگشت به پنل ادمین 🖥')
back_admin.add(ba)

manage_user_btn = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
mub1 = types.KeyboardButton('مدیریت کاربران')
mub2 = types.KeyboardButton('دریافت لیستی از آیدی کاربران')
mub3 = types.KeyboardButton('ارسال پیام همگانی')
mub4 = types.KeyboardButton('بازگشت به منو 🏛')
manage_user_btn.add(mub1, mub2, mub3, mub4)


def ads_sent_c_btn(c_msg_id: int):
    btn_asc = types.InlineKeyboardMarkup(row_width=1)
    btn_asch = types.InlineKeyboardButton(text="مشاهده در کانال", url='https://t.me/'+data['channel']+('/%s'%c_msg_id))
    btn_asc.add(btn_asch)
    return btn_asc

def ads_r_btn(ads_code:int, user_id:int):
    btn_r = types.InlineKeyboardMarkup(row_width=1)
    btn_r_1 = types.InlineKeyboardButton(text="ارسال پیام به مشتری", url=('tg://user?id=%s'%user_id))
    btn_r_2 = types.InlineKeyboardButton(text="گزارش عدم رعایت قوانین⛔", callback_data='report_post')
    btn_r.add(btn_r_1, btn_r_2)
    return btn_r


def bad_post_btn(reporter_user, bad_user, bad_post):
    
    btn_bp = types.InlineKeyboardMarkup(row_width=1)
    btn_bp_1 = types.InlineKeyboardButton(text="مشاهده کاربر گزارش دهنده", url=('tg://user?id=%s'%reporter_user))
    btn_bp_2 = types.InlineKeyboardButton(text="پاک کردن این آگهی", callback_data=('rm_bad_post_%s'% bad_post))
    btn_bp_3 = types.InlineKeyboardButton(text="بلاک کردن کاربر متخلف", callback_data=('block__bad_user_%s'% bad_user))
    btn_bp.add(btn_bp_1, btn_bp_2, btn_bp_3)
    return btn_bp

btn_s = types.InlineKeyboardMarkup(row_width=1)
btn_cl = types.InlineKeyboardButton(text="عضویت در کانال", url='https://t.me/'+data['channel'])
btn_cj = types.InlineKeyboardButton(text="عضو شدم!", callback_data='check_join')
btn_s.add(btn_cl, btn_cj)


def hi_text(name:str) -> str :
    return f'''
سلام {name}
به 🤖بات ”{bot.get_me().first_name}“ خوش اومدی

می تونی تکالیفت ، پروژه های دانشجویی ، مقاله و پایان نامه ،  تایپ و پاورپوینت و یا هرچیز دیگه ای رو به عنوان آگهی ثبت کنی تا در کانال مون به اشتراک بزاریم 😉'''

@bot.callback_query_handler(lambda query: query.data == "check_join")
def process_callback(query):
    
    chc = bot.get_chat_member('@'+data['channel'], query.from_user.id).status
    
    if (chc == 'creator' or chc == 'member' or chc == 'administrator'):
        bot.delete_message(query.from_user.id, query.message.id)
        bot.answer_callback_query(query.id, "عضویت شما تایید شد 🔥", show_alert=True)

        bot.send_message(query.from_user.id, hi_text(query.from_user.first_name), disable_web_page_preview=True, reply_markup=start_btn(query.from_user.id))

    else:
        bot.answer_callback_query(query.id, "هنوز عضو نشدی!", show_alert=True)


@bot.callback_query_handler(lambda query: query.data == "report_post")
def process_callback(query):
    for admin in data['admin']:
        bad_user = int(query.message.json['reply_markup']['inline_keyboard'][0][0]['url'].replace('tg://user?id=', ''))
        
        if (query.from_user.id == bad_user):
            bot.answer_callback_query(query.id, "شما نمی توانید آگهی های خود را گزارش بدهید!", show_alert=True)
            return False
        
        msg = bot.forward_message(admin, '@'+data['channel'], query.message.message_id)
        bot.send_message(admin, ("این پست توسط یکی از کاربران گزارش شده است.\nآیدی کاربر متخلف: %s"%bad_user), disable_web_page_preview=True, reply_markup=bad_post_btn(query.from_user.id, bad_user, msg.forward_from_message_id), reply_to_message_id=msg.message_id)
        bot.answer_callback_query(query.id, "گزارش شما با موفقیت ثبت شد!", show_alert=True)


@bot.callback_query_handler(lambda query: str(query.data).startswith('rm_post_'))
def process_callback(query):
    data_db = DATABASE.get()
    ids = query.data.replace('rm_post_', '').split('_')
    post_id, ads_id = int(ids[0]), str(ids[1])
    try:
        data_db['users_data']["%s" % query.from_user.id]['ads'].pop('%s' % ads_id)
        msg = bot.delete_message('@'+data['channel'], post_id)
        DATABASE.commit(data_db)
        try:
            bot.delete_message(query.from_user.id, query.message.id)
            bot.delete_message(query.from_user.id, (query.message.id - 1))
        except Exception as err:
            print(err)
        bot.answer_callback_query(query.id, "این آگهی با موفقیت حذف شد.", show_alert=True)
    except Exception as err:
        bot.answer_callback_query(query.id, "این آگهی دیگه وجود نداره!", show_alert=True)


@bot.callback_query_handler(lambda query: str(query.data).startswith('rm_bad_post_'))
def process_callback(query):
    bad_post_id = int(query.data.replace('rm_bad_post_', ''))
    
    try:
        msg = bot.delete_message('@'+data['channel'], bad_post_id)
        bot.answer_callback_query(query.id, "این آگهی از چنل حذف شد.", show_alert=True)
    except Exception as err:
        bot.answer_callback_query(query.id, "این آگهی دیگه تو چنل وجود نداره!", show_alert=True)

@bot.callback_query_handler(lambda query: str(query.data).startswith('block__bad_user_'))
def process_callback(query):
    bad_user_id = int(query.data.replace('block__bad_user_',''))
    
    if query.from_user.id == bad_user_id:
        bot.answer_callback_query(query.id, "ادمین عزیز این آگهی رو خودت ثبت کردی.\nنمیتونم خودتو بلاک کنم که!", show_alert=True)
        return False
    
    data_db = DATABASE.get()
    if (data_db['users_data']["%s" % bad_user_id]['block']):
        bot.answer_callback_query(query.id, "این کاربر قبلا بلاک شده", show_alert=True)
    else:
        for ads_i in data_db['users_data']["%s" % bad_user_id]['ads']:
            try:
                ads_id = data_db['users_data']["%s" % bad_user_id]['ads'][ads_i]['id']
                msg = bot.delete_message('@'+data['channel'], int(ads_id))
            except Exception as err:
                print(err)
        data_db['users_data']["%s" % bad_user_id]['ads'] = {}
        data_db['users_data']["%s" % bad_user_id]['block'] = True
        DATABASE.commit(data_db)
        bot.send_message(bad_user_id, "⛔️ شما به علت رعایت نکردن قوانین ما بلاک شده اید!")
        bot.answer_callback_query(query.id, "کاربر مورد نظر بلاک شد!", show_alert=True)


@bot.callback_query_handler(lambda query: str(query.data).startswith('uch_block_'))
def process_callback(query):
    chb = query.data.replace('uch_block_', '').split('_')
    isb = True if chb[0] == 'true' else False
    uid = int(chb[1])
    
    data_db = DATABASE.get()
    data_db['users_data']["%s" % uid]['block'] = (isb == False)
    DATABASE.commit(data_db)
    
    chbb = 'true' if (isb == False) else 'false'
    
    btn_uc = types.InlineKeyboardMarkup(row_width=1)
    btn_uc_0 = types.InlineKeyboardButton(text=("🔒 بلاک کردن کاربر" if chbb == 'false' else "🔓 آنبلاک کردن کاربر"), callback_data=('uch_block_%s_%s' % (chbb, uid)))
    btn_uc.add(btn_uc_0)
    
    bot.edit_message_reply_markup(query.from_user.id, query.message.id, reply_markup=btn_uc)
    
    bot.send_message(uid, ("به لطف یکی از ادمین هامون شما دیگه بلاک نیستی 🥳" if isb else "شما توسط یکی از ادمین هامون از بلاک شدی 🙁"))
    bot.answer_callback_query(query.id, ("✅ کاربر مورد نظر آنبلاک شد!" if isb else "✅ کاربر مورد نظر بلاک شد!"), show_alert=True)
    
@bot.message_handler(content_types=['text', 'video', 'photo', 'audio', 'voice', 'document', 'location', 'contact', 'sticker'])
def robot(user):
    text = user.text
    name = user.chat.first_name
    username = user.chat.username
    msg_id = user.message_id
    user_id = user.chat.id
    id = user.id
    
    addUser(DATABASE, user_id)
    
    data_db = DATABASE.get()
    if (data_db['users_data']["%s"%user_id]['block']):
        bot.send_message(user_id, "⛔️ شما به علت رعایت نکردن قوانین ما بلاک شده اید!")
        return False
    
    bot.send_chat_action(user_id, 'typing')
    
    chc = bot.get_chat_member('@'+data['channel'], user_id).status
    
    if False == (chc == 'creator' or chc == 'member' or chc == 'administrator') :
        bot.send_message(user_id, f'''
به 🤖بات ”{bot.get_me().first_name}“ خوش آمدید
لطفا برای استفاده از ربات ابتدا در کانال ما عضو شوید سپس روی گزینه عضو شدم کلیک نمائید.
''', disable_web_page_preview=True, reply_markup=btn_s)
        return False
        
    data_db = DATABASE.get()
    if data_db['users_data']["%s" % user_id]['status'] != None:
        
        if text == 'انصراف':
            bot.send_message(user_id, 'به منوی اصلی برگشتیم🏛')
            data_db['users_data']["%s" % user_id]['status'] = None
            DATABASE.commit(data_db)
            bot.send_message(user_id, hi_text(name), disable_web_page_preview=True, reply_markup=start_btn(user_id))
        
        
        elif text == 'بازگشت به پنل ادمین 🖥':
            bot.send_message(user_id, 'به پنل ادمین 🖥 برگشتیم🏛', reply_markup=manage_user_btn)
            data_db['users_data']["%s" % user_id]['status'] = None
            DATABASE.commit(data_db)

        data_db = DATABASE.get()
        if data_db['users_data']["%s" % user_id]['status'] == 'get_ads':
            if len(text) >= 320 or len(text) <= 10 :
                bot.send_message(user_id, "متن شما باید بیشتر از 10 کارکتر و  کمتر از 320 کارکتر باشه.\nدوباره تلاش کن!", reply_to_message_id=msg_id, reply_markup=cancel_btn)
            else:
                ads_code = 22343432
                msg = bot.send_message('@'+data['channel'], f"کد آگهی: {ads_code}\n\n{text}\n\n@{data['channel']}", reply_markup=ads_r_btn(ads_code, user_id))
                len_ads = len(data_db['users_data']["%s" % user_id]['ads'])
                data_db['users_data']["%s" % user_id]['ads'][len_ads] = {}
                data_db['users_data']["%s" % user_id]['ads'][len_ads]['id'] = int(msg.message_id)
                data_db['users_data']["%s" % user_id]['ads'][len_ads]['msg'] = text
                
                bot.send_message(user_id, 'آگهی شما با موفقیت در کانال ثبت شد.', reply_markup=ads_sent_c_btn(msg.message_id))
                data_db['users_data']["%s" % user_id]['status'] = None
                DATABASE.commit(data_db)
                bot.send_message(user_id, 'به منوی اصلی برگشتیم🏛', disable_web_page_preview=True, reply_markup=start_btn(user_id))
        
        elif data_db['users_data']["%s" % user_id]['status'] == 'forward-all-user':
            
            len_users = len(data_db['users_id'])
            
            for i in range(len_users):
                tuid = data_db['users_id'][i]
                if tuid in data['admin']:
                    len_users -= 1
                    continue
                msg = bot.forward_message(tuid, user_id, msg_id)
            
            bot.send_message(user_id, ('پیام شما با موفقیت برای %s کاربر ارسال شد.' % len_users))
            data_db['users_data']["%s" % user_id]['status'] = None
            DATABASE.commit(data_db)
            bot.send_message(user_id, 'به پنل ادمین 🖥 برگشتیم🏛', reply_markup=manage_user_btn)
        
        elif data_db['users_data']["%s" % user_id]['status'] == 'manage_user':
            try:
                uid = int(text.strip())
                if uid in data_db['users_id']:
                    if uid in data['admin']:
                        bot.send_message(user_id, 'این کاربر از ادامین ربات می باشد.\n شما اجازه مدیریت او را ندارید!', reply_markup=cancel_btn)
                    else:
                        data_db = DATABASE.get()
                        chd = bot.get_chat(uid)
                        chd_name = chd.first_name if chd.last_name == None else f"{chd.first_name} {chd.last_name}"
                        chd_un = "ندارد" if chd.username == None else ('\n@%s' % chd.username)
                        chd_bio = "ندارد" if chd.bio == None else ('\n%s' % chd.bio)
                        chd_txt = ('''
نام کاربری: %s
آیدی: %s
آیدی عددی: %s
تعداد آگهی های ناتمام: %s
بیوگرافی: %s
''' % (chd_name, chd_un, uid, len(data_db['users_data']["%s" % uid]['ads']), chd_bio))
                        
                        chd_block = 'true' if data_db['users_data']["%s" % uid]['block'] else 'false'
                        
                        btn_uc = types.InlineKeyboardMarkup(row_width=1)
                        btn_uc_0 = types.InlineKeyboardButton(text=("🔒 بلاک کردن کاربر" if chd_block == 'false' else "🔓 آنبلاک کردن کاربر"), callback_data=('uch_block_%s_%s' % (chd_block, uid)))
                        btn_uc.add(btn_uc_0)
                                                
                        prof = bot.get_user_profile_photos(uid)
                        if prof.total_count > 0 :
                            bot.send_photo(user_id, prof.photos[0][0].file_id, caption=chd_txt, reply_markup=btn_uc)
                        else:
                            bot.send_message(user_id, chd_txt, disable_web_page_preview=True, reply_markup=btn_uc)

                else:
                    bot.send_message(user_id, 'این آيدی عددی در دیتابیس کاربران ما وجود نداشت!', reply_markup=back_admin)
            except ValueError as err:
                bot.send_message(user_id, 'این آيدی عددی درست نمی باشد!', reply_markup=back_admin)
        
        return False
    
    if text == '/start' or text == 'بازگشت به منو 🏛':
        
        if text == 'بازگشت به منو 🏛':
            bot.send_message(user_id, 'به منوی اصلی برگشتیم🏛')
    
        bot.send_message(user_id, hi_text(name), disable_web_page_preview=True, reply_markup=start_btn(user_id))

    elif text == 'ثبت آگهی جدید 📇':
        
        data_db = DATABASE.get()
        if len(data_db['users_data']["%s" % user_id]['ads']) >= 50:
            bot.send_message(user_id, 'شما تا الان 50 آگهی ثبت کرده اید.\nشما میتوانید آگهی های پیشین را انجام شده و یا حذف نمایید!', reply_to_message_id=msg_id, reply_markup=start_btn(user_id))
        
        bot.send_message(user_id, f'''
❌ **حتما حتما این متن رو بخونید** ❌

⚖️ راهنما و قوانین ثبت آگهی:

1️⃣ متن آگهی باید برای یک خواسته و نیازمندی باشه یعنی نمیتونی چندتا موضوع مختلف رو توی یه آگهی ثبت کنی. 

2️⃣ توی متن آگهی استفاده از لینک و موارد تبلیغاتی مجاز نیست! ⚠️

3️⃣  استفاده از کلمات مستجهن و توهین آمیز ممنوع است.🔒

4️⃣ از ثبت آگهی های امتحان کوییز و امثال آن جدا خودداری کنید 📛

🔺کانال در راستای کمک و رفع اشکال علمی حرکت میکند و با متقلبین کاملا مخالف است!

❌ در صورتی که آگهی تون قوانین ذکر شده رو رعایت نکرده باشه آگهی از کانال پاک میشه  و هیچ مسولیتی در قبال شما نیست ❌
''', parse_mode='Markdown')
        bot.send_message(user_id, f'''
خب حالا ابتدا متن آگهیت رو بصورت خلاصه برام بفرست.
این متن باید بیشتر از 10 کارکتر و  کمتر از 320 کارکتر باشه.

برای مثال:
کمک در حل چند سوال ریاضی مهندسی
''', reply_markup=cancel_btn)
        
        data_db = DATABASE.get()
        data_db['users_data']["%s" % user_id]['status'] = 'get_ads'
        DATABASE.commit(data_db)

    elif text == 'ثبت آگهی رایگان 💰':
        bot.send_message(user_id, 'بزودی 🙂')

    elif text == 'راهنما 📕' or text == '/help':
        bot.send_message(user_id, f'''
- ** ثبت آگهی**
شما برای ثبت آگهی خود
باید از دکمه [[ثبت آگهی جدید 📇]] استفاده کنید.
همچنین شما میتوانید آگهی خود را بصورت متن ساده برای ما ارسال کنید.

- **عدم رعایت قوانین**
در صورتی که کاربران آگهی شما رو گزارش کنند
و پس از بررسی این موضوع تایید شود آگهی شما پاک شده
و در صورت تکرار شما توسط بات بلاک خواهید شد.

- **مدیریت آگهی ها**
شما برای مدیریت آگهی های خود
باید از دکمه [[مدیریت آگهی ها 🗂]] استفاده کنید.
همچنین شما میتوانید آگهی  های خودتون رو حذف, مشاهده و یا انجام شده ثبت کنید.

موفق باشید.
''', reply_to_message_id=msg_id, parse_mode='Markdown')

    elif text == 'مدیریت آگهی ها 🗂':
        
        data_db = DATABASE.get()
        if len(data_db['users_data']["%s" % user_id]['ads']) > 0:
            for ads in data_db['users_data']["%s" % user_id]['ads']:
                msg = bot.send_message(user_id, ('شماره آگهی : %s \nمتن آگهی:‌ \n%s' % (ads, data_db['users_data']["%s" % user_id]['ads'][ads]['msg'])))
                bot.send_message(user_id, 'در صورتی که آگهی شما انجام شده و به پایان رسیده و یا قصد پاک کردن آن را دارید با استفاده از دکمه پایین میتوانید آگهی خود را حذف نمایید.', reply_to_message_id=msg.message_id,
                    reply_markup=types.InlineKeyboardMarkup(row_width=1).add(
                        types.InlineKeyboardButton(
                            text="❌ پاک کردن آگهی ❌",
                            callback_data=('rm_post_%s_%s' % (data_db['users_data']["%s" % user_id]['ads'][ads]['id'], ads))
                        )
                    )
                )
        else:
            bot.send_message(user_id, 'شما آگهی تا به حال ثبت نکرده اید!')
    
    elif text == 'پنل ادمین 🖥':
        if user_id in data['admin']:
            bot.send_message(user_id, '🔥 پنل ادمین 🔥', reply_markup=manage_user_btn)
        else:
            bot.send_message(user_id, 'شما اجازه دسترسی به این بخش را ندارید!')
    elif text == 'دریافت لیستی از آیدی کاربران':
        if user_id in data['admin']:
            try:
                file_name = f'users-id-(@{bot.get_me().username}).txt'
                with open(file_name, 'w+') as file:
                    data_db = DATABASE.get()
                    file.write('\n'.join([str(data_db['users_id'][i])
                            for i in range(len(data_db['users_id']))]))
                    file.close()
                ufile = open(file_name)
                bot.send_document(
                    user_id, ufile, visible_file_name=file_name, reply_to_message_id=msg_id)
                ufile.close()
                rm_file(file_name)
            except: ...
        else:
            bot.send_message(user_id, 'شما اجازه دسترسی به این بخش را ندارید!')
    
    
    elif text == 'ارسال پیام همگانی':
        if user_id in data['admin']:
            
            bot.send_message(user_id, "کافیه یک پیامی برام بفرستی تا برای تمام کاربران ربات فوروارد کنم.", reply_markup=cancel_btn)
            bot.send_message(user_id, 'تایپ های مجاز: \ntext, video, photo, audio, voice, document, location, contact, sticker')

            data_db = DATABASE.get()
            data_db['users_data']["%s" % user_id]['status'] = 'forward-all-user'
            DATABASE.commit(data_db)
    
        else:
            bot.send_message(user_id, 'شما اجازه دسترسی به این بخش را ندارید!')
    
    elif text == 'مدیریت کاربران':

        if user_id in data['admin']:
                        
            bot.send_message(user_id, "آیدی عددی کاربر مورد نظر رو برام بفرست", reply_markup=back_admin)

            data_db = DATABASE.get()
            data_db['users_data']["%s" % user_id]['status'] = 'manage_user'
            DATABASE.commit(data_db)
    
        else:
            bot.send_message(user_id, 'شما اجازه دسترسی به این بخش را ندارید!')
            

try:
    bot.polling(True) if __name__ == '__main__' else quit(
        '=> python3 fa_ads_telegram_bot')
except Exception as err:
    print(err)