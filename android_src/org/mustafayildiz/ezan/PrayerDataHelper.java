package org.mustafayildiz.ezan;

import android.content.Context;
import android.content.SharedPreferences;

public final class PrayerDataHelper {
    public static final String PREFS = "huzur_prayer_widget";
    private PrayerDataHelper() {}

    public static SharedPreferences prefs(Context context) {
        return context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public static String value(Context context, String key, String fallback) {
        return prefs(context).getString(key, fallback);
    }

    public static boolean enabled(Context context) {
        return prefs(context).getBoolean("persistent_notification", false);
    }

    public static String allTimes(Context context) {
        return "İmsak " + value(context, "Imsak", "--:--") +
                "  Güneş " + value(context, "Gunes", "--:--") +
                "  Öğle " + value(context, "Ogle", "--:--") + "\n" +
                "İkindi " + value(context, "Ikindi", "--:--") +
                "  Akşam " + value(context, "Aksam", "--:--") +
                "  Yatsı " + value(context, "Yatsi", "--:--");
    }
}
