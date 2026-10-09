package org.mustafayildiz.ezan;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;

public class PrayerNotificationService extends Service {
    public static final String CHANNEL_ID = "huzur_prayer_times";
    public static final int NOTIFICATION_ID = 9101;

    @Override public void onCreate() {
        super.onCreate();
        createChannel();
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (!PrayerDataHelper.enabled(this)) {
            stopForeground(true);
            stopSelf();
            return START_NOT_STICKY;
        }
        startForeground(NOTIFICATION_ID, buildNotification());
        PrayerWidgetProvider.updateAll(this);
        return START_STICKY;
    }

    private void createChannel() {
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID,
                    "Namaz Vakitleri", NotificationManager.IMPORTANCE_LOW);
            channel.setDescription("Namaz vakitlerini sessiz ve kalıcı olarak gösterir.");
            channel.setSound(null, null);
            getSystemService(NotificationManager.class).createNotificationChannel(channel);
        }
    }

    private Notification buildNotification() {
        Intent launch = getPackageManager().getLaunchIntentForPackage(getPackageName());
        PendingIntent pending = launch == null ? null : PendingIntent.getActivity(this, 702, launch,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        int icon = getApplicationInfo().icon;
        return new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(icon)
                .setContentTitle("Huzur Vakti | " + PrayerDataHelper.value(this, "location", ""))
                .setContentText(PrayerDataHelper.value(this, "next_text", "Namaz vakitleri"))
                .setStyle(new NotificationCompat.BigTextStyle().bigText(
                        PrayerDataHelper.allTimes(this) + "\n" +
                        PrayerDataHelper.value(this, "next_text", "")))
                .setContentIntent(pending)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .setSilent(true)
                .setCategory(NotificationCompat.CATEGORY_SERVICE)
                .build();
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}
