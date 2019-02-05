import os
import signal

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
        item_quit.connect('activate', quit)
        item_synch.connect('activate', synch)
        menu.append(item_synch)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def quit(source):
        client.send_request(['-q', 'server_shutdown'])
        gtk.main_quit()

    def synch(source):
        client.send_request(['-q', 'synch'])

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('../icon/ec_logo.png'),
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    gtk.main()
