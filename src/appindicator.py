import os
import signal

import client.graphical.gui_handler as configs_gui
from client import client

APPINDICATOR_ID = 'events_collector_indicator_id'


def indicator_main():
    import gi

    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk as gtk

    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as appindicator

    def build_menu():
        menu = gtk.Menu()

        item_quit = gtk.MenuItem('Quit')
        item_synch = gtk.MenuItem('Synch now')
        item_gc_to_trello = gtk.MenuItem('GC -> Trello')
        item_trello_to_gc = gtk.MenuItem('Trello deadlines -> GC')
        item_configs = gtk.MenuItem('Configs')

        item_quit.connect('activate', quit)
        item_synch.connect('activate', synch)
        item_gc_to_trello.connect('activate', gc_to_trello)
        item_trello_to_gc.connect('activate', trello_to_gc)
        item_configs.connect('activate', show_configs)

        menu.append(item_synch)
        menu.append(item_gc_to_trello)
        menu.append(item_trello_to_gc)
        menu.append(item_configs)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def quit(source):
        client.send_request(['-q', 'server_shutdown'])
        gtk.main_quit()

    def synch(source):
        client.send_request(['-q', 'synch'])

    def gc_to_trello(source):
        client.send_request(['-q', 'gc_to_trello'])

    def trello_to_gc(source):
        client.send_request(['-q', 'trello_to_gc'])

    def show_configs(source):
        configs_gui.main()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('../icon/ec_logo.png'),
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()
