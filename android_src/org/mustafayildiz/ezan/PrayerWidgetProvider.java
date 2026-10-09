package org.mustafayildiz.ezan;
import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.widget.RemoteViews;
public class PrayerWidgetProvider extends AppWidgetProvider {
 public static void updateAll(Context c){AppWidgetManager m=AppWidgetManager.getInstance(c);int[] a=m.getAppWidgetIds(new ComponentName(c,PrayerWidgetProvider.class));for(int id:a)update(c,m,id);}
 private static int rid(Context c,String n){return c.getResources().getIdentifier(n,"id",c.getPackageName());}
 private static void update(Context c,AppWidgetManager m,int id){
  RemoteViews v=new RemoteViews(c.getPackageName(),c.getResources().getIdentifier("prayer_widget","layout",c.getPackageName()));
  v.setTextViewText(rid(c,"widget_location"),PrayerDataHelper.value(c,"location","Kayseri / Hacılar"));
  String[] k={"Imsak","Gunes","Ogle","Ikindi","Aksam","Yatsi"};String[] r={"time_imsak","time_gunes","time_ogle","time_ikindi","time_aksam","time_yatsi"};
  for(int i=0;i<k.length;i++)v.setTextViewText(rid(c,r[i]),PrayerDataHelper.value(c,k[i],"--:--"));
  v.setTextViewText(rid(c,"widget_next"),PrayerDataHelper.value(c,"next_text","Sonraki vakit hesaplanıyor"));
  v.setTextViewText(rid(c,"widget_kerahat"),PrayerDataHelper.value(c,"kerahat_text",""));
  boolean active=PrayerDataHelper.prefs(c).getBoolean("kerahat_active",false);
  v.setTextColor(rid(c,"widget_kerahat"),active?Color.rgb(198,35,25):Color.rgb(166,58,8));
  Intent launch=c.getPackageManager().getLaunchIntentForPackage(c.getPackageName());if(launch!=null)v.setOnClickPendingIntent(rid(c,"widget_root"),PendingIntent.getActivity(c,701,launch,PendingIntent.FLAG_UPDATE_CURRENT|PendingIntent.FLAG_IMMUTABLE));
  m.updateAppWidget(id,v);
 }
 @Override public void onUpdate(Context c,AppWidgetManager m,int[] ids){for(int id:ids)update(c,m,id);}
}
