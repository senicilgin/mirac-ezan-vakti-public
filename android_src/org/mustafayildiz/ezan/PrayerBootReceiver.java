package org.mustafayildiz.ezan;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class PrayerBootReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context, Intent intent) {
        PrayerWidgetProvider.updateAll(context);
        if (PrayerDataHelper.enabled(context)) {
            Intent service = new Intent(context, PrayerNotificationService.class);
            if (Build.VERSION.SDK_INT >= 26) context.startForegroundService(service);
            else context.startService(service);
        }
    }
}
