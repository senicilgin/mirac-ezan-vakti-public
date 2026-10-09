package org.mustafayildiz.ezan;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;

import androidx.core.app.NotificationCompat;

/**
 * Miraç Ezan Vakti alarm alıcısı.
 * Telefonun RingerMode veya Rahatsız Etmeyin durumuna dokunmaz.
 * Uygulama sessiz dönemini kendi SharedPreferences alanında tutar.
 */
public class AlarmReceiver extends BroadcastReceiver {
    private static final String PREFS = "mirac_app_audio_state";
    private static final String KEY_SILENT_UNTIL = "silent_until";

    @Override
    public void onReceive(Context context, Intent intent) {
        String action = value(intent, "action", "PRAYER");
        SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);

        if ("SILENCE".equals(action)) {
            if (intent.getBooleanExtra("app_silent_mode", true)) {
                int minutes = Math.max(0, intent.getIntExtra("silent_minutes", 30));
                long until = System.currentTimeMillis() + minutes * 60_000L;
                prefs.edit().putLong(KEY_SILENT_UNTIL, until).apply();
            }
            return;
        }

        if ("RESTORE".equals(action)) {
            prefs.edit().remove(KEY_SILENT_UNTIL).apply();
            return;
        }

        boolean inSilentPeriod = prefs.getLong(KEY_SILENT_UNTIL, 0L)
                > System.currentTimeMillis();
        boolean allowSound = !inSilentPeriod;
        if (inSilentPeriod && "PRE".equals(action)) {
            allowSound = intent.getBooleanExtra("play_pre_in_silent", false);
        } else if (inSilentPeriod && "PRAYER".equals(action)) {
            allowSound = intent.getBooleanExtra("play_prayer_in_silent", true);
        }

        boolean vibration = intent.getBooleanExtra("vibration_enabled", true);
        String audioStream = value(intent, "audio_stream", "ALARM");
        String soundValue = value(intent, "sound_uri", "DEFAULT");
        String title = value(intent, "title", "Miraç Ezan Vakti");
        String message = value(intent, "message", "Namaz vakti bildirimi");
        int notificationId = intent.getIntExtra("id", 2001);

        postNotification(
                context, notificationId, title, message, audioStream,
                soundValue, allowSound, vibration
        );
    }

    private void postNotification(
            Context context,
            int id,
            String title,
            String message,
            String stream,
            String soundValue,
            boolean allowSound,
            boolean vibrationEnabled
    ) {
        NotificationManager manager =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        Uri sound = allowSound ? resolveSound(context, stream, soundValue) : null;
        AudioAttributes attributes = buildAudioAttributes(stream);
        String channelId = "mirac_" + stream.toLowerCase() + "_"
                + (allowSound ? stableSoundId(soundValue) : "silent");

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId,
                    channelName(stream, allowSound),
                    NotificationManager.IMPORTANCE_HIGH
            );
            channel.setDescription("Miraç Ezan Vakti namaz vakti bildirimleri");
            channel.enableLights(true);
            channel.setLightColor(Color.rgb(4, 133, 140));
            channel.enableVibration(vibrationEnabled);
            if (vibrationEnabled) {
                channel.setVibrationPattern(new long[]{0, 450, 220, 450});
            }
            channel.setSound(sound, attributes);
            manager.createNotificationChannel(channel);
        }

        Intent launchIntent = context.getPackageManager()
                .getLaunchIntentForPackage(context.getPackageName());
        PendingIntent contentIntent = null;
        if (launchIntent != null) {
            launchIntent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                flags |= PendingIntent.FLAG_IMMUTABLE;
            }
            contentIntent = PendingIntent.getActivity(context, id, launchIntent, flags);
        }

        NotificationCompat.Builder builder = new NotificationCompat.Builder(context, channelId)
                .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
                .setContentTitle(title)
                .setContentText(message)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(message))
                .setAutoCancel(true)
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC);

        if (contentIntent != null) {
            builder.setContentIntent(contentIntent);
        }

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            if (allowSound && sound != null) {
                builder.setSound(sound, legacyStreamType(stream));
            } else {
                builder.setSound(null);
            }
            if (vibrationEnabled) {
                builder.setVibrate(new long[]{0, 450, 220, 450});
            }
        }

        manager.notify(id, builder.build());
        if (vibrationEnabled && Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            vibrate(context);
        }
    }

    private static AudioAttributes buildAudioAttributes(String stream) {
        int usage;
        if ("MEDIA".equals(stream)) {
            usage = AudioAttributes.USAGE_MEDIA;
        } else if ("NOTIFICATION".equals(stream)) {
            usage = AudioAttributes.USAGE_NOTIFICATION;
        } else {
            usage = AudioAttributes.USAGE_ALARM;
        }
        return new AudioAttributes.Builder()
                .setUsage(usage)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build();
    }

    private static int legacyStreamType(String stream) {
        if ("MEDIA".equals(stream)) {
            return android.media.AudioManager.STREAM_MUSIC;
        }
        if ("NOTIFICATION".equals(stream)) {
            return android.media.AudioManager.STREAM_NOTIFICATION;
        }
        return android.media.AudioManager.STREAM_ALARM;
    }

    private static Uri resolveSound(Context context, String stream, String value) {
        if ("SILENT".equals(value)) {
            return null;
        }
        if (value != null && value.startsWith("PRESET::")) {
            String rawName = value.substring("PRESET::".length())
                    .toLowerCase().replaceAll("[^a-z0-9_]", "_");
            int resId = context.getResources().getIdentifier(
                    rawName, "raw", context.getPackageName());
            if (resId != 0) {
                return Uri.parse("android.resource://" + context.getPackageName() + "/" + resId);
            }
        }
        if ("MEDIA".equals(stream)) {
            return RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        }
        if ("NOTIFICATION".equals(stream)) {
            return RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        }
        return RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM);
    }

    private static String channelName(String stream, boolean sound) {
        String name = "ALARM".equals(stream) ? "Alarm sesi"
                : ("MEDIA".equals(stream) ? "Medya sesi" : "Bildirim sesi");
        return "Miraç Vakti - " + name + (sound ? "" : " (sessiz)");
    }

    private static String stableSoundId(String value) {
        if (value == null || value.length() == 0) {
            return "default";
        }
        return Integer.toHexString(value.hashCode());
    }

    private static String value(Intent intent, String key, String fallback) {
        String result = intent.getStringExtra(key);
        return result == null || result.length() == 0 ? fallback : result;
    }

    private static void vibrate(Context context) {
        Vibrator vibrator = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
        if (vibrator == null || !vibrator.hasVibrator()) {
            return;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(
                    new long[]{0, 450, 220, 450}, -1));
        } else {
            vibrator.vibrate(new long[]{0, 450, 220, 450}, -1);
        }
    }
}
