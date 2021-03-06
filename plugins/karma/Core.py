import os
import pickle
import time

from discord import Embed, Message

from cybot import utils, client

user_data = {}
_karma_file = 'karma.pkl'
_file_loaded = False
_last_karma_time = {}
_time_between_karma = 60 * 30  # half an hour, in seconds


def get_karma_embed(member, karma):
    em = Embed(title="karma balance", color=0x0080ff)
    _url = member.avatar_url
    if _url is None:
        _url = member.default_avatar

    em.set_thumbnail(url=_url)
    em.add_field(name="User: %s" % member.name, value="karma: %d" % karma, inline=False)

    return em


def set_karma_embed(member, karma):
    em = Embed(color=0x00ff40)

    _url = member.avatar_url
    if _url is None:
        _url = member.default_avatar

    em.set_author(name="%s#%s" % (member.name, member.discriminator), icon_url=_url)
    em.set_footer(text="User was given %d karma points!" % karma)

    return em


@utils.register_command(name='give')
async def add_karma_cmd(message: Message, args: [str]):
    """
    give @USER: give 1 karma to a user
    """
    if not _file_loaded:
        load_karma()
    try:
        sender_id = message.author.id
        target_id = message.mentions[0].id
        user_nick = message.mentions[0].nick
        if user_nick is None:
            user_nick = message.mentions[0].name
    except:
        return await client.send_message(message.channel, 'No user specified!')
    if target_id == sender_id:
        return await client.send_message(message.channel, "4ril??")
    if not _eligible_to_give(sender_id, target_id):
        return await client.send_message(message.channel, 'You can give karma to %s again in more %d minutes' %
                                         (user_nick,
                                          (_time_between_karma - (time.time() - _last_karma_time[(sender_id,
                                                                                                  target_id)])) / 60))
    _add_karma(sender_id, target_id)
    await client.send_message(message.channel, '%s has %s karma' % (user_nick, _get_karma(target_id)))


@utils.register_command(name='setkarma')
@utils.admin
async def set_karma_cmd(message: Message, args: [str]):
    """
    setkarma @USER number: set number of karma to user (Admins only)
    """
    if not _file_loaded:
        load_karma()
    try:
        sender_id = message.author.id
        target_id = message.mentions[0].id
        user_nick = message.mentions[0].nick
        if user_nick is None:
            user_nick = message.mentions[0].name
        if not args[1].isnumeric():
            return await client.send_message(message.channel, 'This is not a number')
        num = int(args[1])
    except Exception as e:
        print(e)
        return await client.send_message(message.channel, 'No user specified!')
    _set_karma(sender_id, target_id, num)
    return await client.send_message(message.channel, '', embed=set_karma_embed(message.mentions[0], num))


@utils.register_command(name='take')
@utils.admin
async def take_karma_cmd(message: Message, args: [str]):
    """
    take @USER: take 1 karma to a user (Admins only)
    """
    if not _file_loaded:
        load_karma()
    try:
        user_id = message.mentions[0].id
        user_nick = message.mentions[0].nick
        if user_nick is None:
            user_nick = message.mentions[0].name
    except:
        return await client.send_message(message.channel, 'No user specified!')
    if user_id == message.author.id:
        return await client.send_message(message.channel, "4ril??")
    if not _eligible_to_give(user_id, None):
        return
    _take_karma(user_id)
    return await client.send_message(message.channel, '%s has %s karma' % (user_nick, _get_karma(user_id)))


@utils.register_command(name='karma', channels=['bot'])
async def get_karma_cmd(message: Message, args: [str]):
    """
    karma @USER: check how much karma a user has
    """
    if not _file_loaded:
        load_karma()
    try:
        user_id = message.mentions[0].id
        user_nick = message.mentions[0].nick
        if user_nick is None:
            user_nick = message.mentions[0].name
        ans = get_karma_embed(message.mentions[0], _get_karma(user_id))
    except:
        ans = get_karma_embed(message.author, _get_karma(message.author.id))
    await client.send_message(message.channel, '', embed=ans)


def _set_karma_time(sender_id, target_id):
    t = int(time.time())
    _last_karma_time[(sender_id, target_id)] = t


def _eligible_to_give(sender_id, target_id):
    if (sender_id, target_id) not in _last_karma_time:
        return True
    return (int(time.time()) - _last_karma_time[(sender_id, target_id)]) > _time_between_karma


def _add_karma(sender_id, target_id):
    if target_id not in user_data:
        user_data[target_id] = 1
    else:
        user_data[target_id] += 1
    _set_karma_time(sender_id, target_id)
    save_karma()


def _take_karma(user_id):
    if user_id not in user_data:
        user_data[user_id] = -1
    else:
        user_data[user_id] -= 1
    _set_karma_time(user_id)
    save_karma()


def _set_karma(sender_id, target_id, num=1):
    user_data[target_id] = num
    _set_karma_time(sender_id, target_id)
    save_karma()


def _take_karma(target_id, num=1):
    if target_id not in user_data:
        user_data[target_id] = 0
    else:
        user_data[target_id] -= num
    _set_karma_time(0, target_id)
    save_karma()


def _dec_karma(sender_id, target_id):
    if target_id not in user_data:
        user_data[target_id] = 0
    else:
        user_data[target_id] -= 1
        if user_data[target_id] < 0:
            user_data[target_id] = 0
    _set_karma_time(sender_id, target_id)
    save_karma()


def _get_karma(user_id):
    load_karma()
    if user_id not in user_data:
        return 0
    return user_data[user_id]


def load_karma():
    global _file_loaded
    if _file_loaded:
        return
    if os.path.isfile(_karma_file):
        with open(_karma_file, 'rb') as handle:
            global user_data
            user_data = pickle.load(handle)
    _file_loaded = True


def save_karma():
    with open(_karma_file, 'wb') as handle:
        pickle.dump(user_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
