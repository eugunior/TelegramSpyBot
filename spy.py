from telethon.sync import TelegramClient, events
from telethon.tl.types import UserStatusOnline, UserStatusOffline, ContactStatus
from datetime import datetime, timedelta
from time import sleep, mktime
from config import API_HASH, API_ID, BOT_TOKEN, delay


client = TelegramClient('user', API_ID, API_HASH)
client.connect()
client.start()

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

users_to_track = []


@bot.on(events.NewMessage(pattern='/help'))
async def help(event):
    help_message = [
        '/spy - start tracking users list',
        '/stop - stop tracking users list',
        '/add - add user(s) by username or phone to users list',
        '/clear - clear users list',
        '/help - commands list'
    ]
    await event.respond('\n'.join(help_message))

@bot.on(events.NewMessage(pattern='/add'))
async def add(event):
    message = event.message
    users = message.message.split()[1:]
    users_to_track.extend(users)
    await event.respond(f'✅ user(s) added to list:\n{", ".join(users_to_track)}')

@bot.on(events.NewMessage(pattern='/clear'))
async def clear(event):
    users_to_track.clear()
    await event.respond(f'🗑 users list cleared')

@bot.on(events.NewMessage(pattern='/stop'))
async def stop(event):
    global running
    running = False
    await event.respond(f'🛑 spying stopped')

@bot.on(events.NewMessage(pattern='/spy'))
async def spy(event):
    user_states = {user: {'is_online': None, 
                      'online_start': None, 
                      'offline_start': None, 
                      'online_end': None, 
                      'offline_end': None} for user in users_to_track}
    
    counter = 0
    global running
    running = True

    await event.respond(f'👁‍🗨 spying started')

    while running:
        for user_handler in users_to_track:
            user = await client.get_entity(user_handler)
            state = user_states[user_handler]
            if isinstance(user.status, UserStatusOnline):
                if state['is_online'] != True:
                    state['is_online'] = True
                    state['online_start'] = datetime.now()
                    state['offline_end'] = datetime.now()
                    
                    if state['offline_start'] is None:
                        await event.respond(f'{user_handler} went online🌕\nafter unknown? offline time')
                    else:
                        offline_time =  state['offline_end'] - state['offline_start']
                        await event.respond(f'{user_handler} went online🌕\nafter {offline_time} offline time')
                    
            elif isinstance(user.status, UserStatusOffline):
                if state['is_online'] != False:
                    state['is_online'] = False
                    state['offline_start'] = datetime.now() #state['offline_start'] = normalize_time(user.status.was_online) # it doesn't work precisely
                    state['online_end'] = datetime.now()

                    if state['online_start'] is None: 
                        await event.respond(f'{user_handler} went offline🌑\nafter unknown? online time')
                    else:
                        online_time =  state['online_end'] - state['online_start']
                        await event.respond(f'{user_handler} went offline🌑\nafter {online_time} online time')
        counter += 1
        print(f'spying on {len(users_to_track)} users: {counter}')
        sleep(delay)

def normalize_time(date):
    pivot = mktime(date.timetuple())
    offset = datetime.fromtimestamp(pivot) - datetime.utcfromtimestamp(pivot)
    local_date = date + offset
    naive_date = str(local_date).split('+')[0]
    date = datetime.fromisoformat(naive_date)
    return date

def main():
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()