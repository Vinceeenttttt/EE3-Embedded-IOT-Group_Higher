package com.example.iotproject;

import android.content.Intent;
import android.media.Ringtone;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Vibrator;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.TextView;
import android.widget.Toast;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;

public class MainActivity extends AppCompatActivity {

    //User Defined Parameters

    static String MQTTHOST = "tcp://ee-estott-octo.ee.ic.ac.uk:1883";
    static String TOPIC1 = "IC.embedded/HIGHER/tem";
    static String TOPIC2 = "IC.embedded/HIGHER/hum";
    static String TOPIC3 = "IC.embedded/HIGHER/com";

    //Customizable threshold

    static String HumThreshold = "50%";
    static String TemThreshold = "75C";


    MqttAndroidClient client;

    //Three Textview to display information

    TextView subText;
    TextView subText2;
    TextView subText3;

    //Three Arraylist to store past activities / data for other uses

    ArrayList<String> TemData = new ArrayList<>();
    ArrayList<String> HumData = new ArrayList<>();
    ArrayList<String> ComData = new ArrayList<>();

    MqttConnectOptions options;

    Vibrator vibrator;

    Ringtone myRingtone;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);



        setContentView(R.layout.activity_main);

        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,WindowManager.LayoutParams.FLAG_FULLSCREEN);

        subText = (TextView)findViewById(R.id.subText);
        subText2 = (TextView)findViewById(R.id.subText2);
        subText3 = (TextView)findViewById(R.id.subText3);

        vibrator = (Vibrator) getSystemService(VIBRATOR_SERVICE);

        Uri uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        myRingtone = RingtoneManager.getRingtone(getApplicationContext(),uri);

        String clientId = MqttClient.generateClientId();
        client = new MqttAndroidClient(MainActivity.this, MQTTHOST, clientId);

        options = new MqttConnectOptions();

        //Different version of mqtt could be used, need to be changed to most suitable one

        //options.setMqttVersion(MqttConnectOptions.MQTT_VERSION_3_1);

        options.setCleanSession(true);
        options.setConnectionTimeout(10);
        options.setKeepAliveInterval(20);


        try {

            InputStream input =
                    MainActivity.this.getAssets().open("iot.eclipse.org.bks");


            options.setSocketFactory(client.getSSLSocketFactory(input, "eclipse-password"));


            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                //Server successfully connected
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"connected", Toast.LENGTH_LONG).show();
                    setSubscription();

                }

                @Override
                //Server connection failed / firewall problems
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"connection failed", Toast.LENGTH_LONG).show();


                }
            });


        } catch (MqttException | IOException e) {
            e.printStackTrace();
        }


        //Call back functions
        client.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {

            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {

                //Subscribed to three different topics
                //System alerts when threshold reached

                if(topic.equals(TOPIC1)){
                    subText.setText(new String(message.getPayload()));
                    TemData.add(new String(message.getPayload()));

                    if(subText.equals(TemThreshold)){
                        vibrator.vibrate(500);
                        myRingtone.play();
                    }
                }

                if(topic.equals(TOPIC2)){
                    subText2.setText(new String(message.getPayload()));
                    HumData.add(new String(message.getPayload()));

                    if(subText2.equals(HumThreshold)){
                        vibrator.vibrate(500);
                        myRingtone.play();
                    }
                }

                else if(topic.equals(TOPIC3)){
                    subText3.setText(new String(message.getPayload()));
                    ComData.add(new String(message.getPayload()));

                    //if device sends 1, meaning reading has reached threshold
                    //phone alerts user, sends notification
                    if(subText3.equals("1")){
                        vibrator.vibrate(500);
                        myRingtone.play();
                    }
                }

                vibrator.vibrate(500);


            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });
    }

    //Publish function can be used in the future to execute different instructions

    public void publish(View v){
        String topic = "IC.embedded/HIGHER";
        String message = "HEY";
        try {
            client.publish(topic, message.getBytes(),0,false);
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }


    //Define subscriptions
    private void setSubscription(){
        try{
            client.subscribe(TOPIC1,1);
            client.subscribe(TOPIC2,1);
            client.subscribe(TOPIC3,1);

        }catch(MqttException e){
            e.printStackTrace();
        }
    }

    public void conn(View v){
        try {
            IMqttToken token = client.connect(options);
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"connected", Toast.LENGTH_LONG).show();
                    setSubscription();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"connection failed", Toast.LENGTH_LONG).show();

                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }

    public void disconn(View v){
        try {
            IMqttToken token = client.disconnect();
            token.setActionCallback(new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Toast.makeText(MainActivity.this,"disconnected", Toast.LENGTH_LONG).show();

                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Toast.makeText(MainActivity.this,"could not disconnect..", Toast.LENGTH_LONG).show();

                }
            });
        } catch (MqttException e) {
            e.printStackTrace();
        }
    }


    @Override
    protected void onDestroy() {
        super.onDestroy();
        client.unregisterResources();
        client.close();
    };
}
