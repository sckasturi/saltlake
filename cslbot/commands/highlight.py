# Copyright (C) 2013-2015 Samuel Damashek, Peter Foley, James Forcier, Srijay Kasturi, Reed Koser, Christopher Reffett, and Fox Wilson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from time import localtime, strftime
from ..helpers import arguments
from ..helpers.orm import Log
from ..helpers.command import Command


def get_last(cursor, nick):
    return cursor.query(Log).filter(Log.source.ilike(nick), Log.type != 'join').order_by(Log.time.desc()).first()


@Command('highlight', ['db', 'nick', 'config', 'target', 'botnick'])
def cmd(send, msg, args):
    """When a nick was last pinged.
    Syntax: {command} [nick]
    """
    parser = arguments.ArgParser(args['config'])
    parser.add_argument('nick', nargs='?', action=arguments.NickParser)
    try:
        cmdargs = parser.parse_args(msg)
    except arguments.ArgumentException as e:
        send(str(e))
        return
    if not cmdargs.nick:
        cmdargs.nick = args['nick']
    row = args['db'].query(Log).filter(Log.msg.ilike("%" + cmdargs.nick + "%"), ~Log.msg.contains('%shighlight' % args['config']['core']['cmdchar']),
                                       Log.target == args['target'], Log.source != args['botnick'], Log.source != cmdargs.nick,
                                       Log.type != 'mode', Log.type != 'nick').order_by(Log.time.desc()).first()
    if row is None:
        send("%s has never been pinged." % cmdargs.nick)
    else:
        time = strftime('%Y-%m-%d %H:%M:%S', localtime(row.time))
        send("<%s> %s: %s" % (time, row.source, row.msg))