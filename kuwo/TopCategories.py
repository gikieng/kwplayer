

from gi.repository import GdkPixbuf
from gi.repository import Gtk

from kuwo import Net
from kuwo import Widgets


class TopCategories(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.app = app
        self.first_show = False

        self.buttonbox = Gtk.Box()
        self.pack_start(self.buttonbox, False, False, 0)

        self.button_main = Gtk.Button('热门分类')
        self.button_main.connect('clicked', self.on_button_main_clicked)
        self.buttonbox.pack_start(self.button_main, False, False, 0)

        self.button_sub1 = Gtk.Button('')
        self.button_sub1.connect('clicked', self.on_button_sub1_clicked)
        self.buttonbox.pack_start(self.button_sub1, False, False, 0)

        self.button_sub2 = Gtk.Button('')
        self.button_sub2.connect('clicked', self.on_button_sub2_clicked)
        self.buttonbox.pack_start(self.button_sub2, False, False, 0)

        self.label = Gtk.Label('')
        self.buttonbox.pack_start(self.label, False, False, 0)

        # checked, name, artist, album, rid, artistid, albumid
        self.liststore_songs = Gtk.ListStore(bool, str, str, str,
                int, int, int)
        self.control_box = Widgets.ControlBox(self.liststore_songs, app)
        self.buttonbox.pack_end(self.control_box, False, False, 0)

        self.scrolled_main = Gtk.ScrolledWindow()
        self.pack_start(self.scrolled_main, True, True, 0)
        # logo, name, nid, num of lists(info)
        self.liststore_main = Gtk.ListStore(GdkPixbuf.Pixbuf, str, int, str)
        iconview_main = Widgets.IconView(self.liststore_main)
        iconview_main.connect('item_activated', 
                self.on_iconview_main_item_activated)
        self.scrolled_main.add(iconview_main)

        self.scrolled_sub1 = Gtk.ScrolledWindow()
        self.scrolled_sub1.get_vadjustment().connect('value-changed',
                self.on_scrolled_sub1_scrolled)
        self.pack_start(self.scrolled_sub1, True, True, 0)
        # logo, name, nid, num of lists(info)
        self.liststore_sub1 = Gtk.ListStore(GdkPixbuf.Pixbuf, str, int, str)
        iconview_sub1 = Widgets.IconView(self.liststore_sub1, tooltip=1)
        iconview_sub1.connect('item_activated', 
                self.on_iconview_sub1_item_activated)
        self.scrolled_sub1.add(iconview_sub1)

        self.scrolled_sub2 = Gtk.ScrolledWindow()
        self.scrolled_sub2.get_vadjustment().connect('value-changed',
                self.on_scrolled_sub2_scrolled)
        self.pack_start(self.scrolled_sub2, True, True, 0)
        # logo, name, nid, info
        self.liststore_sub2 = Gtk.ListStore(GdkPixbuf.Pixbuf, str, int, str)
        iconview_sub2 = Widgets.IconView(self.liststore_sub2, tooltip=1)
        iconview_sub2.connect('item_activated', 
                self.on_iconview_sub2_item_activated)
        self.scrolled_sub2.add(iconview_sub2)

        self.scrolled_songs = Gtk.ScrolledWindow()
        self.pack_start(self.scrolled_songs, True, True, 0)
        self.scrolled_songs.get_vadjustment().connect('value-changed',
                self.on_scrolled_songs_scrolled)
        treeview_songs = Widgets.TreeViewSongs(self.liststore_songs, app)
        self.scrolled_songs.add(treeview_songs)

    def after_init(self):
        self.buttonbox.hide()
        self.scrolled_sub1.hide()
        self.scrolled_sub2.hide()
        self.scrolled_songs.hide()

    def first(self):
        if self.first_show:
            return
        self.first_show = True

        nid = 5
        page = 0
        nodes, total_page = Net.get_nodes(nid, page)
        if nodes is None:
            print('Failed to get nodes, do something!')
            return
        i = 0
        for node in nodes:
            self.liststore_main.append([self.app.theme['anonymous'],
                node['disname'], int(node['id']), node['info'], ])
            Net.update_liststore_image(self.liststore_main, i, 0, 
                    node['pic'])
            i += 1

    def on_iconview_main_item_activated(self, iconview, path):
        model = iconview.get_model()
        self.curr_sub1_name = model[path][1]
        self.curr_sub1_id = model[path][2]
        if self.curr_sub1_id in (79, 17250):
            self.use_sub2 = True
        else:
            self.use_sub2 = False
        self.label.set_label(self.curr_sub1_name)
        self.show_sub1(init=True)

    def show_sub1(self, init=False):
        if init:
            self.scrolled_main.hide()
            self.buttonbox.show_all()
            self.button_sub1.hide()
            self.button_sub2.hide()
            self.control_box.hide()
            self.scrolled_sub1.get_vadjustment().set_value(0)
            self.scrolled_sub1.show_all()
            self.sub1_page = 0
            self.liststore_sub1.clear()
        nodes, self.sub1_total = Net.get_nodes(self.curr_sub1_id,
                self.sub1_page)
        if nodes is None:
            return
        i = len(self.liststore_sub1)
        for node in nodes:
            _id = 'id' if self.use_sub2 else 'sourceid'
            self.liststore_sub1.append([self.app.theme['anonymous'],
                node['name'], int(node[_id]), node['info'], ])
            Net.update_liststore_image(self.liststore_sub1, i, 0, 
                    node['pic'])
            i += 1

    def on_iconview_sub1_item_activated(self, iconview, path):
        model = iconview.get_model()
        if self.use_sub2:
            self.curr_sub2_name = model[path][1]
            self.curr_sub2_id = model[path][2]
            self.label.set_label(self.curr_sub2_name)
            self.button_sub1.set_label(self.curr_sub1_name)
            self.show_sub2(init=True)
        else:
            self.curr_list_name = model[path][1]
            self.curr_list_id = model[path][2]
            self.label.set_label(self.curr_list_name)
            self.button_sub1.set_label(self.curr_sub1_name)
            self.show_songs(init=True)

    def show_sub2(self, init=False):
        if init:
            self.scrolled_sub1.hide()
            self.button_sub1.show_all()
            self.scrolled_sub2.get_vadjustment().set_value(0)
            self.scrolled_sub2.show_all()
            self.sub2_page = 0
            self.liststore_sub2.clear()
        nodes, self.sub2_total = Net.get_nodes(self.curr_sub2_id, 
                self.sub2_page)
        if nodes is None:
            print('Error: nodes is empty')
            return
        i = len(self.liststore_sub2)
        for node in nodes:
            self.liststore_sub2.append([self.app.theme['anonymous'],
                node['name'], int(node['sourceid']), node['info'], ])
            Net.update_liststore_image(self.liststore_sub2, i, 0, 
                    node['pic'])
            i += 1


    def on_iconview_sub2_item_activated(self, iconview, path):
        model = iconview.get_model()
        self.curr_list_name = model[path][1]
        self.curr_list_id = model[path][2]
        self.label.set_label(self.curr_list_name)
        self.button_sub2.set_label(self.curr_sub2_name)
        print('sub2 item activated, will call show song()')
        self.show_songs(init=True)

    def show_songs(self, init=False):
        print('show songs')
        if init:
            self.songs_page = 0
            self.scrolled_sub1.hide()
            self.button_sub1.show_all()
            self.control_box.show_all()
            if self.use_sub2:
                self.scrolled_sub2.hide()
                self.button_sub2.show_all()
            self.scrolled_songs.get_vadjustment().set_value(0.0)
            self.scrolled_songs.show_all()
            self.liststore_songs.clear()

        songs, self.songs_total = Net.get_themes_songs(self.curr_list_id, 
                self.songs_page)
        if songs is None:
            return
        if len(songs) == 0:
            songs_wrap = Net.get_album(self.curr_list_id)
            self.songs_total = 1
            if songs_wrap is None:
                return
            songs = songs_wrap['musiclist']
            for song in songs:
                self.liststore_songs.append([
                    True, song['name'], song['artist'], songs_wrap['name'], 
                    int(song['id']), int(song['artistid']), 
                    int(songs_wrap['albumid']), ])
            return
        for song in songs:
            self.liststore_songs.append([
                True, song['name'], song['artist'], song['album'],
                int(song['id']), int(song['artistid']), 
                int(song['albumid']), ])

    # buttonbox
    def on_button_main_clicked(self, btn):
        self.scrolled_sub1.hide()
        self.scrolled_sub2.hide()
        self.scrolled_songs.hide()
        self.buttonbox.hide()
        self.scrolled_main.show_all()

    def on_button_sub1_clicked(self, btn):
        self.scrolled_songs.hide()
        self.scrolled_sub2.hide()
        self.button_sub1.hide()
        self.button_sub2.hide()
        self.control_box.hide()
        self.label.set_label(self.button_sub1.get_label())
        self.scrolled_sub1.show_all()

    def on_button_sub2_clicked(self, btn):
        self.scrolled_songs.hide()
        self.button_sub2.hide()
        self.control_box.hide()
        self.label.set_label(self.button_sub2.get_label())
        self.scrolled_sub2.show_all()


    # scrolled windows
    def on_scrolled_sub1_scrolled(self, adj):
        if Widgets.reach_scrolled_bottom(adj) and \
                self.sub1_page < self.sub1_total - 1:
            self.sub1_page += 1
            self.show_sub1()

    def on_scrolled_sub2_scrolled(self, adj):
        if Widgets.reach_scrolled_bottom(adj) and \
                self.sub2_page < self.sub2_total - 1:
            self.sub2_page += 1
            self.show_sub2()

    def on_scrolled_songs_scrolled(self, adj):
        if Widgets.reach_scrolled_bottom(adj) and \
                self.songs_page < self.songs_total - 1:
            self.songs_page += 1
            self.show_songs()
