# -*- coding: utf-8 -*-
"""Miraç Ezan Vakti

Telefon başına bağımsız ayarlar, ilk kurulum sihirbazı ve Android geri
hareketi desteği içeren sadeleştirilmiş, temiz ana uygulama dosyası.
"""

import json
import math
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle, Triangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

try:
    from widget_notification_bridge import sync_prayer_surface, request_pin_widget
except Exception:
    def sync_prayer_surface(app):
        return False

    def request_pin_widget():
        return False


API = "https://ezanvakti.emushaf.net"
COUNTRY_ID = "2"
APP_VERSION = "1.1.0"

BG = (0.91, 0.96, 0.96, 1)
GREEN = (0.015, 0.52, 0.55, 1)
DARK = (0.015, 0.30, 0.33, 1)
MINT = (0.74, 0.92, 0.93, 1)
WHITE = (1, 1, 1, 1)
TEXT = (0.16, 0.18, 0.18, 1)
MUTED = (0.38, 0.43, 0.43, 1)
GOLD = (0.95, 0.67, 0.10, 1)
RED = (0.72, 0.25, 0.22, 1)
KAABA_LAT, KAABA_LON = 21.422487, 39.826206
AUDIO_EXTS = (".wav", ".ogg", ".mp3", ".m4a", ".aac")

PRAYERS = [
    ("İmsak", "Imsak", "moon"),
    ("Güneş", "Gunes", "sun"),
    ("Öğle", "Ogle", "sun_high"),
    ("İkindi", "Ikindi", "cloud"),
    ("Akşam", "Aksam", "sunset"),
    ("Yatsı", "Yatsi", "moon_star"),
]

PROVINCES = {
    "Adana": (37.0000, 35.3213), "Adıyaman": (37.7648, 38.2786),
    "Afyonkarahisar": (38.7507, 30.5567), "Ağrı": (39.7191, 43.0503),
    "Amasya": (40.6499, 35.8353), "Ankara": (39.9334, 32.8597),
    "Antalya": (36.8969, 30.7133), "Artvin": (41.1828, 41.8183),
    "Aydın": (37.8560, 27.8416), "Balıkesir": (39.6484, 27.8826),
    "Bilecik": (40.0567, 30.0665), "Bingöl": (38.8853, 40.4983),
    "Bitlis": (38.3938, 42.1232), "Bolu": (40.5760, 31.5788),
    "Burdur": (37.7203, 30.2908), "Bursa": (40.1950, 29.0600),
    "Çanakkale": (40.1553, 26.4142), "Çankırı": (40.6013, 33.6134),
    "Çorum": (40.5506, 34.9556), "Denizli": (37.7765, 29.0864),
    "Diyarbakır": (37.9144, 40.2306), "Edirne": (41.6818, 26.5623),
    "Elazığ": (38.6810, 39.2264), "Erzincan": (39.7500, 39.5000),
    "Erzurum": (39.9000, 41.2700), "Eskişehir": (39.7767, 30.5206),
    "Gaziantep": (37.0662, 37.3833), "Giresun": (40.9128, 38.3895),
    "Gümüşhane": (40.4603, 39.4814), "Hakkari": (37.5833, 43.7333),
    "Hatay": (36.4018, 36.3498), "Isparta": (37.7648, 30.5566),
    "Mersin": (36.8121, 34.6415), "İstanbul": (41.0082, 28.9784),
    "İzmir": (38.4192, 27.1287), "Kars": (40.6013, 43.0975),
    "Kastamonu": (41.3887, 33.7827), "Kayseri": (38.7312, 35.4787),
    "Kırklareli": (41.7351, 27.2252), "Kırşehir": (39.1425, 34.1709),
    "Kocaeli": (40.8533, 29.8815), "Konya": (37.8746, 32.4932),
    "Kütahya": (39.4167, 29.9833), "Malatya": (38.3552, 38.3095),
    "Manisa": (38.6191, 27.4289), "Kahramanmaraş": (37.5858, 36.9371),
    "Mardin": (37.3212, 40.7245), "Muğla": (37.2153, 28.3636),
    "Muş": (38.9462, 41.7539), "Nevşehir": (38.6939, 34.6857),
    "Niğde": (37.9667, 34.6833), "Ordu": (40.9839, 37.8764),
    "Rize": (41.0201, 40.5234), "Sakarya": (40.7731, 30.3948),
    "Samsun": (41.2867, 36.3300), "Siirt": (37.9333, 41.9500),
    "Sinop": (42.0231, 35.1531), "Sivas": (39.7477, 37.0179),
    "Tekirdağ": (40.9833, 27.5167), "Tokat": (40.3167, 36.5500),
    "Trabzon": (41.0015, 39.7178), "Tunceli": (39.1079, 39.5401),
    "Şanlıurfa": (37.1674, 38.7955), "Uşak": (38.6823, 29.4082),
    "Van": (38.4891, 43.4089), "Yozgat": (39.8181, 34.8147),
    "Zonguldak": (41.4564, 31.7987), "Aksaray": (38.3687, 34.0370),
    "Bayburt": (40.2552, 40.2249), "Karaman": (37.1759, 33.2287),
    "Kırıkkale": (39.8468, 33.5153), "Batman": (37.8812, 41.1351),
    "Şırnak": (37.4187, 42.4918), "Bartın": (41.6344, 32.3375),
    "Ardahan": (41.1105, 42.7022), "Iğdır": (39.9167, 44.0333),
    "Yalova": (40.6500, 29.2667), "Karabük": (41.2061, 32.6204),
    "Kilis": (36.7184, 37.1212), "Osmaniye": (37.0742, 36.2478),
    "Düzce": (40.8438, 31.1565),
}

KAYSERI_DISTRICTS = (
    "Akkışla", "Bünyan", "Develi", "Felahiye", "Hacılar", "İncesu",
    "Kocasinan", "Melikgazi", "Özvatan", "Pınarbaşı", "Sarıoğlan",
    "Sarız", "Talas", "Tomarza", "Yahyalı", "Yeşilhisar",
)

DISTRICTS = {
    ("Kayseri", "Hacılar"): (38.6463, 35.4494),
    ("Kayseri", "Kocasinan"): (38.7330, 35.4850),
    ("Kayseri", "Melikgazi"): (38.7219, 35.4933),
    ("Kayseri", "Talas"): (38.6908, 35.5538),
    ("Kayseri", "Develi"): (38.3906, 35.4922),
    ("Kayseri", "Yahyalı"): (38.1023, 35.3573),
    ("Kayseri", "Bünyan"): (38.8463, 35.8603),
    ("Kayseri", "Pınarbaşı"): (38.7222, 36.3931),
    ("Kayseri", "İncesu"): (38.6224, 35.1826),
}


def rounded(widget, color=WHITE, radius=22, border=None):
    with widget.canvas.before:
        Color(*color)
        widget._bg = RoundedRectangle(pos=widget.pos, size=widget.size, radius=[dp(radius)])
        if border:
            Color(*border)
            widget._border = Line(rounded_rectangle=(*widget.pos, *widget.size, dp(radius)), width=1)

    def update(*_):
        widget._bg.pos, widget._bg.size = widget.pos, widget.size
        if hasattr(widget, "_border"):
            widget._border.rounded_rectangle = (*widget.pos, *widget.size, dp(radius))

    widget.bind(pos=update, size=update)
    return widget


def lbl(text, color=TEXT, size="15sp", markup=False, **kwargs):
    obj = Label(text=text, color=color, font_size=size, markup=markup, **kwargs)
    obj.bind(size=lambda w, v: setattr(w, "text_size", (v[0], None)))
    return obj


class FlatButton(Button):
    def __init__(self, bg=GREEN, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", bg)
        kwargs.setdefault("color", WHITE)
        super().__init__(**kwargs)


class CanvasIcon(Widget):
    def __init__(self, icon="home", color=GREEN, **kwargs):
        super().__init__(**kwargs)
        self.icon = icon
        self.icon_color = color
        self.bind(pos=self.redraw, size=self.redraw)
        Clock.schedule_once(self.redraw, 0)

    def redraw(self, *_):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        s = max(dp(1), min(w, h))
        cx, cy = x + w / 2, y + h / 2
        c = self.icon_color
        width = max(dp(2), s * .05)
        with self.canvas:
            Color(*c)
            if self.icon == "home":
                Line(points=[cx-s*.3, cy, cx, cy+s*.28, cx+s*.3, cy], width=width)
                Line(rectangle=(cx-s*.22, cy-s*.25, s*.44, s*.26), width=width)
            elif self.icon == "clock":
                Line(circle=(cx, cy, s*.3), width=width)
                Line(points=[cx, cy, cx, cy+s*.16, cx+s*.14, cy-s*.08], width=width)
            elif self.icon == "compass":
                Line(circle=(cx, cy, s*.3), width=width)
                Triangle(points=[cx, cy+s*.25, cx-s*.1, cy-s*.1, cx+s*.1, cy-s*.1])
            elif self.icon == "tasbih":
                for i in range(12):
                    a = math.radians(i * 30)
                    bx = cx + math.cos(a) * s*.23
                    by = cy + math.sin(a) * s*.23
                    Ellipse(pos=(bx-s*.035, by-s*.035), size=(s*.07, s*.07))
            elif self.icon == "settings":
                Line(circle=(cx, cy, s*.13), width=width)
                Line(circle=(cx, cy, s*.27), width=width)
            elif self.icon == "pin":
                Line(circle=(cx, cy+s*.08, s*.16), width=width)
                Line(points=[cx-s*.14, cy, cx, cy-s*.3, cx+s*.14, cy], width=width)
            elif self.icon in ("moon", "moon_star"):
                Ellipse(pos=(cx-s*.25, cy-s*.25), size=(s*.5, s*.5))
                Color(*WHITE)
                Ellipse(pos=(cx-s*.05, cy-s*.1), size=(s*.38, s*.38))
            elif self.icon in ("sun", "sun_high", "sunset"):
                Ellipse(pos=(cx-s*.13, cy-s*.13), size=(s*.26, s*.26))
                for i in range(8):
                    a = math.radians(i * 45)
                    Line(points=[cx+math.cos(a)*s*.19, cy+math.sin(a)*s*.19,
                                 cx+math.cos(a)*s*.29, cy+math.sin(a)*s*.29], width=width)
            elif self.icon == "cloud":
                Line(points=[cx-s*.28, cy-s*.1, cx+s*.28, cy-s*.1], width=width)
                Line(circle=(cx-s*.1, cy, s*.18, 10, 170), width=width)


class IconButton(BoxLayout):
    def __init__(self, title, icon, callback, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(2), **kwargs)
        self.callback = callback
        self.add_widget(CanvasIcon(icon=icon, color=GREEN))
        self.add_widget(lbl(title, size="11sp", bold=True, size_hint_y=None, height=dp(23)))
        self.bind(on_touch_down=self._touch)

    def _touch(self, _, touch):
        if self.collide_point(*touch.pos):
            self.callback()
            return True
        return False


class EzanApp(App):
    """Telefon başına bağımsız ayarlı ana uygulama."""

    def build(self):
        Window.clearcolor = BG
        self.root_dir = Path(__file__).resolve().parent
        self.user_dir = Path(self.user_data_dir)
        self.user_dir.mkdir(parents=True, exist_ok=True)

        self.settings_file = self.user_dir / "settings.json"
        self.times_file = self.user_dir / "times.json"
        self.tasbih_file = self.user_dir / "tasbih.json"

        self.settings = self.load(self.settings_file, self.defaults())
        self.migrate_settings()
        self.times = self.load(self.times_file, [])
        self.tasbih = self.load(self.tasbih_file, {
            "count": 0, "total": 0, "target": 33,
            "phrase": "Sübhanallah", "date": date.today().isoformat(), "daily": 0,
        })

        self.sound_dirs = [
            self.root_dir / "ses_kutuphanesi",
            self.root_dir / "sounds",
            self.root_dir / "assets" / "sounds",
            self.root_dir / "audio",
            self.user_dir / "sounds",
        ]
        # APK içindeki klasörler salt okunabilir olabilir. Sadece kullanıcı dizini oluşturulur.
        (self.user_dir / "sounds").mkdir(parents=True, exist_ok=True)
        self.sound_catalog = self.scan_sounds()
        self.preview_sound = None
        self.compass_active = False
        self.navigation_history = []
        self.current_screen = None
        self.active_popup = None

        brand = self.root_dir / "assets" / "mirac_vakti_icon.png"
        if brand.exists():
            self.icon = str(brand)

        self.root_box = BoxLayout(orientation="vertical")
        self.body = BoxLayout()
        self.root_box.add_widget(self.body)
        self.root_box.add_widget(self.bottom_nav())

        Window.bind(on_keyboard=self.on_keyboard)

        if self.settings.get("setup_completed", False):
            self.ensure_times()
            self.navigate("home", add_history=False)
            Clock.schedule_once(lambda *_: self.start_android_services_after_setup(), 1.2)
        else:
            self.show_setup_wizard(0)

        Clock.schedule_interval(self.update_countdown, 1)
        Clock.schedule_interval(lambda *_: self.sync_android_surfaces_safe(), 60)
        return self.root_box

    @staticmethod
    def defaults():
        return {
            "setup_completed": False,
            "setup_step": 0,
            "city": "",
            "district": "",
            "location_mode": "manual",
            "persistent_notification": True,
            "app_silent_mode": True,
            "silent_mode_vibration": True,
            "silent_audio_stream": "ALARM",
            "play_pre_sound_during_silent": False,
            "play_prayer_sound_during_silent": True,
            "global_time_offset": 0,
            "prayer_offsets": {k: 0 for _, k, _ in PRAYERS},
            "kerahat_sunrise_minutes": 45,
            "kerahat_noon_minutes": 10,
            "kerahat_sunset_minutes": 45,
            "enabled": {k: True for _, k, _ in PRAYERS},
            "pre_enabled": {k: True for _, k, _ in PRAYERS},
            "pre": {k: 10 for _, k, _ in PRAYERS},
            "silent_enabled": {k: True for _, k, _ in PRAYERS},
            "silent": {k: 30 for _, k, _ in PRAYERS},
            "pre_sound": {k: "DEFAULT" for _, k, _ in PRAYERS},
            "prayer_sound": {k: "DEFAULT" for _, k, _ in PRAYERS},
        }

    @staticmethod
    def load(path, default):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            return value if isinstance(value, type(default)) else default
        except Exception:
            return default

    @staticmethod
    def save(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)

    def migrate_settings(self):
        defaults = self.defaults()
        # Eski bilgisayar varsayılanlarını ilk kurulum tamamlanmadıysa taşımıyoruz.
        for key, value in defaults.items():
            if key not in self.settings or not isinstance(self.settings[key], type(value)):
                self.settings[key] = value.copy() if isinstance(value, dict) else value
        if "first_run" in self.settings and not self.settings.get("setup_completed"):
            self.settings["setup_completed"] = False
        for _, key, _ in PRAYERS:
            for group in ("enabled", "pre_enabled", "pre", "silent_enabled", "silent",
                          "pre_sound", "prayer_sound", "prayer_offsets"):
                self.settings[group].setdefault(key, defaults[group][key])
        self.save(self.settings_file, self.settings)

    def is_android(self):
        return os.environ.get("ANDROID_ARGUMENT") is not None

    def clear(self):
        self.stop_compass()
        self.body.clear_widgets()

    def scroll(self):
        scroll = ScrollView(bar_width=dp(3))
        content = BoxLayout(orientation="vertical", size_hint_y=None, padding=dp(15), spacing=dp(13))
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        self.body.add_widget(scroll)
        return content

    def header(self, title):
        box = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(10), spacing=dp(8))
        rounded(box, WHITE, 18, MINT)
        logo_path = self.root_dir / "assets" / "mirac_vakti_icon.png"
        if logo_path.exists():
            box.add_widget(Image(source=str(logo_path), size_hint_x=None, width=dp(52)))
        box.add_widget(lbl("[b]Miraç Ezan Vakti[/b]", markup=True, size="20sp", halign="left"))
        box.add_widget(lbl(title, color=GREEN, size="16sp", bold=True, size_hint_x=.55))
        return box

    def bottom_nav(self):
        nav = BoxLayout(size_hint_y=None, height=dp(82), padding=(dp(8), dp(5)), spacing=dp(8))
        rounded(nav, WHITE, 0)
        for title, icon, screen in [
            ("NAMAZ", "home", "home"),
            ("KUR'AN", "clock", "quran"),
            ("KIBLE", "compass", "qibla"),
            ("TESBİH", "tasbih", "tasbih"),
            ("AYARLAR", "settings", "settings"),
        ]:
            nav.add_widget(IconButton(title, icon, lambda s=screen: self.navigate(s)))
        return nav

    def navigate(self, screen, add_history=True):
        if not self.settings.get("setup_completed", False):
            return
        if add_history and self.current_screen and self.current_screen != screen:
            self.navigation_history.append(self.current_screen)
        self.current_screen = screen
        screens = {
            "home": self.show_home,
            "quran": self.show_quran,
            "qibla": self.show_qibla,
            "tasbih": self.show_tasbih,
            "settings": self.show_settings,
            "location": self.show_location_settings,
            "notifications": self.show_notification_settings,
            "silent": self.show_silent_settings,
            "widget": self.show_widget_settings,
            "permissions": self.show_permissions,
        }
        screens.get(screen, self.show_home)()

    def on_keyboard(self, _window, key, *_args):
        if key != 27:
            return False
        if self.active_popup:
            popup = self.active_popup
            self.active_popup = None
            popup.dismiss()
            return True
        if not self.settings.get("setup_completed", False):
            step = int(self.settings.get("setup_step", 0))
            if step > 0:
                self.show_setup_wizard(step - 1)
                return True
            return False
        if self.navigation_history:
            previous = self.navigation_history.pop()
            self.navigate(previous, add_history=False)
            return True
        if self.current_screen != "home":
            self.navigate("home", add_history=False)
            return True
        # Ana ekranda olayı Android'e bırakır, uygulama zorla stop edilmez.
        return False

    def show_setup_wizard(self, step=0):
        self.clear()
        self.current_screen = "setup"
        self.settings["setup_step"] = max(0, min(4, int(step)))
        self.save(self.settings_file, self.settings)
        c = self.scroll()
        c.add_widget(self.header(f"Kurulum {step + 1}/5"))

        if step == 0:
            card = self.setup_card("Hoş Geldiniz",
                "Bu kurulum yalnız bu telefona ait konum, bildirim, ses ve widget tercihlerini kaydeder. Bilgisayardaki ayarlar kullanılmaz.")
            button = FlatButton(text="BAŞLA", size_hint_y=None, height=dp(56))
            button.bind(on_release=lambda *_: self.show_setup_wizard(1))
            card.add_widget(button)
            c.add_widget(card)
        elif step == 1:
            card = self.setup_card("Konumunuzu Seçin", "Namaz vakitleri bu telefonda seçilen konuma göre hesaplanacaktır.")
            city = Spinner(text=self.settings.get("city") or "Kayseri", values=tuple(sorted(PROVINCES)),
                           size_hint_y=None, height=dp(54), background_normal="", background_color=MINT, color=TEXT)
            district = Spinner(text=self.settings.get("district") or "Hacılar", values=tuple(sorted(KAYSERI_DISTRICTS)),
                               size_hint_y=None, height=dp(54), background_normal="", background_color=MINT, color=TEXT)
            city.bind(text=lambda _, value: self.update_setup_district(district, value))
            card.add_widget(lbl("İl", halign="left", size_hint_y=None, height=dp(28)))
            card.add_widget(city)
            card.add_widget(lbl("İlçe", halign="left", size_hint_y=None, height=dp(28)))
            card.add_widget(district)
            button = FlatButton(text="KONUMU KAYDET", size_hint_y=None, height=dp(56))
            button.bind(on_release=lambda *_: self.setup_save_location(city.text, district.text))
            card.add_widget(button)
            c.add_widget(card)
        elif step == 2:
            card = self.setup_card("Bildirim Tercihleri", "Her vakit için bildirim açık gelir. Ön uyarı süresini şimdi seçebilirsiniz; daha sonra Ayarlar'dan değiştirebilirsiniz.")
            self.setup_notifications_check = CheckBox(active=True, size_hint_x=None, width=dp(48))
            row = BoxLayout(size_hint_y=None, height=dp(52))
            row.add_widget(self.setup_notifications_check)
            row.add_widget(lbl("Vakit bildirimleri açık", halign="left"))
            card.add_widget(row)
            self.setup_pre_minutes = TextInput(text="10", input_filter="int", multiline=False,
                                               size_hint_y=None, height=dp(52), background_normal="", background_color=MINT)
            card.add_widget(lbl("Ön uyarı dakikası", halign="left", size_hint_y=None, height=dp(28)))
            card.add_widget(self.setup_pre_minutes)
            button = FlatButton(text="DEVAM ET", size_hint_y=None, height=dp(56))
            button.bind(on_release=self.setup_save_notifications)
            card.add_widget(button)
            c.add_widget(card)
        elif step == 3:
            card = self.setup_card("Android İzinleri", "Bildirimlerin zamanında çalışması için bildirim ve kesin alarm izinlerini kullanıcı onayıyla açın.")
            notify = FlatButton(text="BİLDİRİM İZNİ VER", size_hint_y=None, height=dp(52))
            notify.bind(on_release=lambda *_: self.open_permission_setting("notifications"))
            alarm = FlatButton(text="KESİN ALARM AYARINI AÇ", size_hint_y=None, height=dp(52), bg=DARK)
            alarm.bind(on_release=lambda *_: self.open_permission_setting("exact_alarm"))
            card.add_widget(notify)
            card.add_widget(alarm)
            next_button = FlatButton(text="İZİNLERİ SONRA DA TAMAMLAYABİLİRİM", size_hint_y=None, height=dp(56), bg=(.42,.47,.46,1))
            next_button.bind(on_release=lambda *_: self.show_setup_wizard(4))
            card.add_widget(next_button)
            c.add_widget(card)
        else:
            card = self.setup_card("Kurulum Özeti",
                f"Konum: {self.settings.get('city')} / {self.settings.get('district')}\n"
                f"Bildirimler: {'Açık' if any(self.settings['enabled'].values()) else 'Kapalı'}\n"
                f"Üst bildirim: {'Açık' if self.settings.get('persistent_notification') else 'Kapalı'}")
            persistent_row = BoxLayout(size_hint_y=None, height=dp(54))
            self.setup_persistent = CheckBox(active=True, size_hint_x=None, width=dp(48))
            persistent_row.add_widget(self.setup_persistent)
            persistent_row.add_widget(lbl("Üst bildirimde sıradaki vakti göster", halign="left"))
            card.add_widget(persistent_row)
            button = FlatButton(text="KURULUMU TAMAMLA", size_hint_y=None, height=dp(58))
            button.bind(on_release=self.finish_setup)
            card.add_widget(button)
            c.add_widget(card)

    def setup_card(self, title, description):
        card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(430), padding=dp(18), spacing=dp(12))
        rounded(card, WHITE, 24, MINT)
        card.add_widget(lbl(f"[b]{title}[/b]", markup=True, size="23sp", size_hint_y=None, height=dp(48)))
        card.add_widget(lbl(description, color=MUTED, size="14sp", halign="left", valign="middle", size_hint_y=None, height=dp(100)))
        return card

    def setup_save_location(self, city, district):
        self.settings["city"] = city
        self.settings["district"] = district if city == "Kayseri" else "Merkez"
        self.save(self.settings_file, self.settings)
        self.show_setup_wizard(2)

    def setup_save_notifications(self, *_):
        enabled = bool(self.setup_notifications_check.active)
        try:
            minutes = max(0, min(120, int(self.setup_pre_minutes.text or 10)))
        except ValueError:
            minutes = 10
        for _, key, _ in PRAYERS:
            self.settings["enabled"][key] = enabled
            self.settings["pre_enabled"][key] = enabled
            self.settings["pre"][key] = minutes
        self.save(self.settings_file, self.settings)
        self.show_setup_wizard(3)

    def finish_setup(self, *_):
        if not self.settings.get("city"):
            self.settings["city"] = "Kayseri"
            self.settings["district"] = "Hacılar"
        self.settings["persistent_notification"] = bool(getattr(self, "setup_persistent", None).active)
        self.settings["setup_completed"] = True
        self.settings["setup_step"] = 0
        self.save(self.settings_file, self.settings)
        self.ensure_times(True)
        self.navigation_history.clear()
        self.navigate("home", add_history=False)
        Clock.schedule_once(lambda *_: self.start_android_services_after_setup(), .8)

    def start_android_services_after_setup(self):
        self.ask_runtime_permissions()
        self.schedule_all_alarms()
        self.sync_android_surfaces_safe()

    @staticmethod
    def update_setup_district(spinner, city):
        spinner.values = tuple(sorted(KAYSERI_DISTRICTS)) if city == "Kayseri" else ("Merkez",)
        spinner.text = spinner.values[0]

    def current_coords(self):
        city = self.settings.get("city") or "Kayseri"
        district = self.settings.get("district") or "Merkez"
        return DISTRICTS.get((city, district), PROVINCES.get(city, PROVINCES["Kayseri"]))

    def show_home(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Vakit"))
        city = self.settings.get("city") or "Konum seçilmedi"
        district = self.settings.get("district") or ""
        c.add_widget(lbl(f"[b]{city} / {district}[/b]", markup=True, size="17sp", size_hint_y=None, height=dp(40)))
        card = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(220), padding=dp(18), spacing=dp(8))
        rounded(card, GREEN, 26)
        self.next_title = lbl("Sonraki Vakit", color=WHITE, size="23sp", bold=True)
        self.countdown = lbl("00:00:00", color=WHITE, size="48sp", bold=True)
        card.add_widget(self.next_title)
        card.add_widget(self.countdown)
        c.add_widget(card)
        rec = self.effective_record(self.today_record())
        row = BoxLayout(size_hint_y=None, height=dp(125), spacing=dp(5))
        for title, key, icon in PRAYERS:
            panel = BoxLayout(orientation="vertical", padding=dp(5), spacing=dp(2))
            rounded(panel, WHITE, 14, MINT)
            panel.add_widget(CanvasIcon(icon=icon, color=GREEN, size_hint_y=None, height=dp(34)))
            panel.add_widget(lbl(title, size="11sp", bold=True))
            panel.add_widget(lbl(rec.get(key, "--:--"), size="14sp", bold=True))
            row.add_widget(panel)
        c.add_widget(row)
        self.update_countdown()

    def today_record(self):
        return next((x for x in self.times if x.get("date") == date.today().isoformat()), None)

    @staticmethod
    def shift_time_text(time_text, minutes):
        try:
            hour, minute = map(int, time_text.split(":"))
            total = (hour * 60 + minute + int(minutes)) % 1440
            return f"{total // 60:02d}:{total % 60:02d}"
        except Exception:
            return time_text

    def effective_time(self, record, key):
        global_offset = int(self.settings.get("global_time_offset", 0))
        prayer_offset = int(self.settings.get("prayer_offsets", {}).get(key, 0))
        return self.shift_time_text(record.get(key, "--:--"), global_offset + prayer_offset)

    def effective_record(self, record):
        if not record:
            return {}
        result = dict(record)
        for _, key, _ in PRAYERS:
            result[key] = self.effective_time(record, key)
        return result

    def next_prayer(self):
        now = datetime.now()
        for offset in (0, 1):
            target_day = date.today() + timedelta(days=offset)
            record = next((x for x in self.times if x.get("date") == target_day.isoformat()), None)
            if not record:
                continue
            for title, key, _ in PRAYERS:
                try:
                    hour, minute = map(int, self.effective_time(record, key).split(":"))
                    target = datetime.combine(target_day, datetime.min.time()).replace(hour=hour, minute=minute)
                    if target > now:
                        return title, key, target
                except Exception:
                    continue
        return "İmsak", "Imsak", now + timedelta(hours=1)

    def update_countdown(self, *_):
        if not hasattr(self, "countdown"):
            return
        title, _, target = self.next_prayer()
        seconds = max(0, int((target - datetime.now()).total_seconds()))
        self.next_title.text = f"{title} Vakti"
        self.countdown.text = f"{seconds//3600:02d}:{(seconds%3600)//60:02d}:{seconds%60:02d}"

    def show_settings(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Ayarlar"))
        for text, screen in [
            ("Konum Ayarları", "location"),
            ("Hatırlatma Ayarları", "notifications"),
            ("Vakitlerde Sessize Al", "silent"),
            ("Üst Bildirim ve Widget", "widget"),
            ("İzin Kontrolü", "permissions"),
        ]:
            button = FlatButton(text=text, size_hint_y=None, height=dp(58), bg=WHITE, color=TEXT)
            button.bind(on_release=lambda _, s=screen: self.navigate(s))
            c.add_widget(button)
        reset = FlatButton(text="İLK KURULUMU YENİDEN BAŞLAT", size_hint_y=None, height=dp(56), bg=RED)
        reset.bind(on_release=self.reset_setup)
        c.add_widget(reset)

    def reset_setup(self, *_):
        self.settings = self.defaults()
        self.save(self.settings_file, self.settings)
        self.times = []
        self.save(self.times_file, self.times)
        self.navigation_history.clear()
        self.show_setup_wizard(0)

    def show_location_settings(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Konum Ayarları"))
        city = Spinner(text=self.settings.get("city") or "Kayseri", values=tuple(sorted(PROVINCES)),
                       size_hint_y=None, height=dp(54), background_normal="", background_color=MINT, color=TEXT)
        districts = tuple(sorted(KAYSERI_DISTRICTS)) if city.text == "Kayseri" else ("Merkez",)
        district = Spinner(text=self.settings.get("district") or districts[0], values=districts,
                           size_hint_y=None, height=dp(54), background_normal="", background_color=MINT, color=TEXT)
        city.bind(text=lambda _, value: self.update_setup_district(district, value))
        c.add_widget(city)
        c.add_widget(district)
        save_button = FlatButton(text="KONUMU KAYDET", size_hint_y=None, height=dp(56))
        save_button.bind(on_release=lambda *_: self.save_location_settings(city.text, district.text))
        c.add_widget(save_button)

    def save_location_settings(self, city, district):
        self.settings["city"] = city
        self.settings["district"] = district if city == "Kayseri" else "Merkez"
        self.save(self.settings_file, self.settings)
        self.ensure_times(True)
        self.sync_android_surfaces_safe()
        self.navigation_history.clear()
        self.navigate("settings", add_history=False)

    def show_notification_settings(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Hatırlatma Ayarları"))
        self.notification_widgets = {}
        for title, key, _ in PRAYERS:
            row = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(8), spacing=dp(8))
            rounded(row, WHITE, 16, MINT)
            enabled = CheckBox(active=self.settings["enabled"][key], size_hint_x=None, width=dp(48))
            pre = TextInput(text=str(self.settings["pre"][key]), input_filter="int", multiline=False,
                            size_hint_x=None, width=dp(76), background_normal="", background_color=MINT)
            row.add_widget(enabled)
            row.add_widget(lbl(title, halign="left"))
            row.add_widget(pre)
            row.add_widget(lbl("dk", size_hint_x=None, width=dp(32)))
            self.notification_widgets[key] = (enabled, pre)
            c.add_widget(row)
        save_button = FlatButton(text="KAYDET", size_hint_y=None, height=dp(56))
        save_button.bind(on_release=self.save_notification_settings)
        c.add_widget(save_button)

    def save_notification_settings(self, *_):
        for _, key, _ in PRAYERS:
            enabled, pre = self.notification_widgets[key]
            self.settings["enabled"][key] = bool(enabled.active)
            try:
                self.settings["pre"][key] = max(0, min(120, int(pre.text or 10)))
            except ValueError:
                self.settings["pre"][key] = 10
        self.save(self.settings_file, self.settings)
        self.schedule_all_alarms()
        self.navigate("settings", add_history=False)

    def show_silent_settings(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Sessiz Mod"))
        self.silent_mode_check = CheckBox(active=self.settings.get("app_silent_mode", True), size_hint_x=None, width=dp(48))
        row = BoxLayout(size_hint_y=None, height=dp(60))
        row.add_widget(self.silent_mode_check)
        row.add_widget(lbl("Uygulamanın kendi bildirim seslerini yönet", halign="left"))
        c.add_widget(row)
        save_button = FlatButton(text="KAYDET", size_hint_y=None, height=dp(56))
        save_button.bind(on_release=lambda *_: self.save_silent_settings())
        c.add_widget(save_button)

    def save_silent_settings(self):
        self.settings["app_silent_mode"] = bool(self.silent_mode_check.active)
        self.save(self.settings_file, self.settings)
        self.schedule_all_alarms()
        self.navigate("settings", add_history=False)

    def show_widget_settings(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Widget ve Üst Bildirim"))
        self.persistent_check = CheckBox(active=self.settings.get("persistent_notification", True), size_hint_x=None, width=dp(48))
        row = BoxLayout(size_hint_y=None, height=dp(60))
        row.add_widget(self.persistent_check)
        row.add_widget(lbl("Üst bildirimde sıradaki vakti göster", halign="left"))
        c.add_widget(row)
        save_button = FlatButton(text="KAYDET VE YENİLE", size_hint_y=None, height=dp(56))
        save_button.bind(on_release=self.save_widget_settings)
        c.add_widget(save_button)
        widget_button = FlatButton(text="ANA EKRANA WIDGET EKLE", size_hint_y=None, height=dp(56), bg=DARK)
        widget_button.bind(on_release=self.add_prayer_widget)
        c.add_widget(widget_button)

    def save_widget_settings(self, *_):
        self.settings["persistent_notification"] = bool(self.persistent_check.active)
        self.save(self.settings_file, self.settings)
        self.sync_android_surfaces_safe()
        self.navigate("settings", add_history=False)

    def show_permissions(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("İzin Kontrolü"))
        definitions = [
            ("Bildirim izni", "notifications"),
            ("Kesin alarm izni", "exact_alarm"),
            ("Pil optimizasyonu", "battery"),
        ]
        for title, key in definitions:
            button = FlatButton(text=title, size_hint_y=None, height=dp(58), bg=WHITE, color=TEXT)
            button.bind(on_release=lambda _, k=key: self.open_permission_setting(k))
            c.add_widget(button)

    def ask_runtime_permissions(self):
        if not self.is_android():
            return
        try:
            from android.permissions import Permission, request_permissions
            permissions = []
            try:
                permissions.append(Permission.POST_NOTIFICATIONS)
            except AttributeError:
                pass
            if permissions:
                request_permissions(permissions)
        except Exception:
            pass

    def open_permission_setting(self, permission_key):
        if not self.is_android():
            self.alert("Bilgi", "Bu ayar Android cihazda kullanılabilir.")
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            Build = autoclass("android.os.Build")
            context = PythonActivity.mActivity
            package_name = context.getPackageName()
            if permission_key == "notifications" and Build.VERSION.SDK_INT >= 33:
                try:
                    from android.permissions import Permission, request_permissions
                    request_permissions([Permission.POST_NOTIFICATIONS])
                    return
                except Exception:
                    pass
            if permission_key == "exact_alarm" and Build.VERSION.SDK_INT >= 31:
                intent = Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM)
                intent.setData(Uri.parse("package:" + package_name))
            elif permission_key == "battery":
                intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                intent.setData(Uri.parse("package:" + package_name))
            else:
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                intent.setData(Uri.parse("package:" + package_name))
            context.startActivity(intent)
        except Exception as error:
            self.alert("İzin Ayarı", str(error))

    def show_quran(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Kur'an-ı Kerim"))
        c.add_widget(lbl("Kur'an okuma ekranı için internet bağlantısı gerekir.", color=MUTED,
                         size_hint_y=None, height=dp(60)))
        open_button = FlatButton(text="KUR'AN SAYFASINI AÇ", size_hint_y=None, height=dp(56))
        open_button.bind(on_release=lambda *_: self.open_web_url("https://kuran.diyanet.gov.tr"))
        c.add_widget(open_button)

    def open_web_url(self, url):
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as error:
            self.alert("Bağlantı", str(error))

    def show_qibla(self):
        self.clear()
        c = self.scroll()
        c.add_widget(self.header("Kıble"))
        lat, lon = self.current_coords()
        angle = self.qibla_bearing(lat, lon)
        c.add_widget(lbl(f"Kıble açısı: {angle:.1f}°", size="26sp", bold=True,
                         size_hint_y=None, height=dp(100)))
        c.add_widget(lbl("Telefon pusulasını kullanarak kuzeyden saat yönünde bu açıya dönün.",
                         color=MUTED, size_hint_y=None, height=dp(90)))

    @staticmethod
    def qibla_bearing(lat, lon):
        lat1, lat2 = math.radians(lat), math.radians(KAABA_LAT)
        diff = math.radians(KAABA_LON - lon)
        y = math.sin(diff) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(diff)
        return (math.degrees(math.atan2(y, x)) + 360) % 360

    def stop_compass(self):
        self.compass_active = False

    def show_tasbih(self):
        self.clear()
        self.check_tasbih_day()
        c = self.scroll()
        c.add_widget(self.header("Tesbih"))
        panel = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(300), padding=dp(15))
        rounded(panel, GREEN, 28)
        self.tasbih_counter = FlatButton(text=str(self.tasbih["count"]), bg=(0,0,0,0), font_size="72sp")
        self.tasbih_counter.bind(on_release=self.increment_tasbih)
        panel.add_widget(self.tasbih_counter)
        c.add_widget(panel)
        controls = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(8))
        undo = FlatButton(text="GERİ AL", bg=(.4,.46,.43,1))
        undo.bind(on_release=self.undo_tasbih)
        reset = FlatButton(text="SIFIRLA", bg=RED)
        reset.bind(on_release=self.reset_tasbih)
        controls.add_widget(undo)
        controls.add_widget(reset)
        c.add_widget(controls)

    def check_tasbih_day(self):
        today = date.today().isoformat()
        if self.tasbih.get("date") != today:
            self.tasbih["date"] = today
            self.tasbih["daily"] = 0

    def increment_tasbih(self, *_):
        self.tasbih["count"] += 1
        self.tasbih["total"] += 1
        self.tasbih["daily"] += 1
        if self.tasbih["count"] >= self.tasbih["target"]:
            self.tasbih["count"] = 0
            self.vibrate(.2)
        self.save(self.tasbih_file, self.tasbih)
        self.show_tasbih()

    def undo_tasbih(self, *_):
        for key in ("count", "total", "daily"):
            self.tasbih[key] = max(0, int(self.tasbih.get(key, 0)) - 1)
        self.save(self.tasbih_file, self.tasbih)
        self.show_tasbih()

    def reset_tasbih(self, *_):
        self.tasbih["count"] = 0
        self.save(self.tasbih_file, self.tasbih)
        self.show_tasbih()

    @staticmethod
    def vibrate(seconds):
        try:
            from plyer import vibrator
            vibrator.vibrate(seconds)
        except Exception:
            pass

    def scan_sounds(self):
        result = {"Varsayılan Android Sesi": "DEFAULT", "Sessiz": "SILENT"}
        for folder in self.sound_dirs:
            if not folder.exists():
                continue
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix.lower() in AUDIO_EXTS:
                    result[path.stem.replace("_", " ").title()] = "FILE::" + str(path)
        return result

    def ensure_times(self, force=False):
        if self.times and not force and self.today_record():
            return
        lat, lon = self.current_coords()
        self.times = [self.calculate_day(date.today() + timedelta(days=i), lat, lon) for i in range(-1, 63)]
        self.save(self.times_file, self.times)
        if self.settings.get("setup_completed"):
            self.schedule_all_alarms()

    @staticmethod
    def calculate_day(day, lat, lon):
        number = day.timetuple().tm_yday
        lng_hour = lon / 15

        def calc(sunrise, zenith):
            t = number + ((6-lng_hour)/24 if sunrise else (18-lng_hour)/24)
            mean = .9856*t - 3.289
            longitude = (mean + 1.916*math.sin(math.radians(mean)) +
                         .020*math.sin(math.radians(2*mean)) + 282.634) % 360
            ascension = math.degrees(math.atan(.91764*math.tan(math.radians(longitude)))) % 360
            ascension += math.floor(longitude/90)*90 - math.floor(ascension/90)*90
            ascension /= 15
            sin_dec = .39782*math.sin(math.radians(longitude))
            cos_dec = math.cos(math.asin(sin_dec))
            cos_hour = ((math.cos(math.radians(zenith)) - sin_dec*math.sin(math.radians(lat))) /
                        (cos_dec*math.cos(math.radians(lat))))
            hour = math.degrees(math.acos(max(-1, min(1, cos_hour))))
            hour = (360-hour if sunrise else hour) / 15
            return (hour+ascension-.06571*t-6.622-lng_hour+3) % 24

        sunrise = calc(True, 90.833)
        sunset = calc(False, 90.833)
        noon = (sunrise + sunset) / 2
        values = {
            "Imsak": calc(True, 108), "Gunes": sunrise, "Ogle": noon,
            "Ikindi": noon+(sunset-noon)*.55, "Aksam": sunset,
            "Yatsi": calc(False, 107),
        }

        def fmt(value):
            minutes = int(round(value*60)) % 1440
            return f"{minutes//60:02d}:{minutes%60:02d}"

        return {"date": day.isoformat(), **{key: fmt(value) for key, value in values.items()}}

    def schedule_all_alarms(self):
        if not self.is_android() or not self.times or not self.settings.get("setup_completed"):
            return
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Intent = autoclass("android.content.Intent")
            PendingIntent = autoclass("android.app.PendingIntent")
            AlarmManager = autoclass("android.app.AlarmManager")
            AlarmReceiver = autoclass("org.mustafayildiz.ezan.AlarmReceiver")
            context = PythonActivity.mActivity
            manager = context.getSystemService(context.ALARM_SERVICE)
            now = datetime.now()
            request_code = 1000
            for record in self.times:
                for title, key, _ in PRAYERS:
                    if not self.settings["enabled"].get(key, True):
                        continue
                    try:
                        prayer_time = datetime.strptime(
                            record["date"] + " " + self.effective_time(record, key), "%Y-%m-%d %H:%M")
                    except Exception:
                        continue
                    if prayer_time <= now:
                        continue
                    intent = Intent(context, AlarmReceiver)
                    intent.putExtra("action", "PRAYER")
                    intent.putExtra("title", "Miraç Ezan Vakti")
                    intent.putExtra("message", f"{title} vakti girdi")
                    intent.putExtra("id", request_code)
                    intent.putExtra("prayer_key", key)
                    pending = PendingIntent.getBroadcast(
                        context, request_code, intent,
                        PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE)
                    trigger = int(prayer_time.timestamp() * 1000)
                    try:
                        manager.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pending)
                    except Exception:
                        manager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, trigger, pending)
                    request_code += 1
        except Exception as error:
            print("Alarm planlama hatası:", error)

    def sync_android_surfaces_safe(self):
        if not self.settings.get("setup_completed"):
            return False
        try:
            return bool(sync_prayer_surface(self))
        except Exception as error:
            print("Widget ve üst bildirim eşitleme hatası:", error)
            return False

    def add_prayer_widget(self, *_):
        if not self.is_android():
            self.alert("Widget", "Widget yalnız Android APK sürümünde kullanılabilir.")
            return
        try:
            if not request_pin_widget():
                self.alert("Widget", "Ana ekrana uzun basın ve Widget'lar bölümünden Miraç Ezan Vakti'ni seçin.")
        except Exception as error:
            self.alert("Widget", str(error))

    def on_pause(self):
        return True

    def on_resume(self):
        if self.settings.get("setup_completed"):
            Clock.schedule_once(lambda *_: self.sync_android_surfaces_safe(), .8)

    def alert(self, title, message):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10))
        content.add_widget(lbl(message, halign="center", valign="middle"))
        close = FlatButton(text="KAPAT", size_hint_y=None, height=dp(50))
        content.add_widget(close)
        popup = Popup(title=title, content=content, size_hint=(.88, .45), auto_dismiss=False)
        self.active_popup = popup
        close.bind(on_release=lambda *_: self.dismiss_popup(popup))
        popup.open()

    def dismiss_popup(self, popup):
        self.active_popup = None
        popup.dismiss()


if __name__ == "__main__":
    EzanApp().run()
