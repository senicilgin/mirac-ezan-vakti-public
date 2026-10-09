# -*- coding: utf-8 -*-
import os
from datetime import datetime

def is_android():
    return os.environ.get("ANDROID_ARGUMENT") is not None

def sync_prayer_surface(app):
    if not is_android(): return False
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Intent = autoclass("android.content.Intent")
        Build = autoclass("android.os.Build")
        Service = autoclass("org.mustafayildiz.ezan.PrayerNotificationService")
        Widget = autoclass("org.mustafayildiz.ezan.PrayerWidgetProvider")
        context = PythonActivity.mActivity
        record = app.effective_record(app.today_record()) if hasattr(app, "effective_record") else (app.today_record() or {})
        title, _, target = app.next_prayer()
        seconds = max(0, int((target - datetime.now()).total_seconds()))
        next_text = f"Sonraki: {title} | {seconds // 3600:02d}:{(seconds % 3600) // 60:02d} kaldı"
        kerahat = app.current_kerahat() if hasattr(app, "current_kerahat") else None
        if kerahat:
            kerahat_text = f"KERAHAT: {kerahat[0]} {kerahat[1]}-{kerahat[2]}"
        elif hasattr(app, "kerahat_periods"):
            kerahat_text = " | ".join(f"{x[0]} {x[1]}-{x[2]}" for x in app.kerahat_periods())
        else:
            kerahat_text = ""
        prefs = context.getSharedPreferences("huzur_prayer_widget", 0)
        editor = prefs.edit()
        editor.putString("location", f"{app.settings['city']} / {app.settings['district']}")
        for key in ("Imsak", "Gunes", "Ogle", "Ikindi", "Aksam", "Yatsi"):
            editor.putString(key, record.get(key, "--:--"))
        editor.putString("next_text", next_text)
        editor.putString("kerahat_text", kerahat_text)
        editor.putBoolean("kerahat_active", bool(kerahat))
        enabled = bool(app.settings.get("persistent_notification", False))
        editor.putBoolean("persistent_notification", enabled)
        editor.apply()
        Widget.updateAll(context)
        service_intent = Intent(context, Service)
        if enabled:
            if Build.VERSION.SDK_INT >= 26: context.startForegroundService(service_intent)
            else: context.startService(service_intent)
        else: context.stopService(service_intent)
        return True
    except Exception as error:
        print("Widget/bildirim eşitleme hatası:", error)
        return False

def request_pin_widget():
    if not is_android(): return False
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Manager = autoclass("android.appwidget.AppWidgetManager")
        ComponentName = autoclass("android.content.ComponentName")
        Provider = autoclass("org.mustafayildiz.ezan.PrayerWidgetProvider")
        context = PythonActivity.mActivity
        manager = Manager.getInstance(context)
        if not manager.isRequestPinAppWidgetSupported(): return False
        manager.requestPinAppWidget(ComponentName(context, Provider), None, None)
        return True
    except Exception as error:
        print("Widget sabitleme hatası:", error)
        return False
