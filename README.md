# EE3-Embedded-IOT-Group_Higher

## Introduction

This is an Internet-Of-Things project designed for baby cradle beds. Rasperberry Pi and Android application have been used.

## Raspberry Pi

After you install the operating system and connect your Pi to your network, you'll need to locate it so you can `ssh` into it and run some commands.

The default "Raspbian" OS will automatically broadcast its presence on your network under the mDNS name "raspberrypi". If you are using Mac or Linux, you can reach your Pi easily:

```sh
ssh pi@raspberrypi.local
```

> Note that in SSH is disabled by default in recent version of Raspbian; [see this page for instructions to re-enable it](https://www.raspberrypi.org/blog/a-security-update-for-raspbian-pixel/).

The default username for Raspbian is `pi` and the password is `raspberry`.

## Basic setup preparations

Once you're logged into your Pi, you should begin by updating the default system packages (note that these commands may be different if you are not running Raspbian OS).

```sh
sudo apt-get update
sudo apt-get upgrade
```

For OSMC or other stripped down Raspberry OS, you may need to install git and make
```sh
sudo apt-get install git make
```
## TLS protocal


IoT is, of course, all about connecting to the Internet, as much as it is about security. Therefor, encryption becomes essential to secure communication. To do this, we firstly need to get a broker certificate which could be downloaded from (https://test.mosquitto.org/ssl/mosquitto.org.crt).

Generate a certificate signing request by:

```sh
openssl req -out client.csr -key client.key -new
```

After this, you can securely reconnect the broker by adding security information before connecting:
```sh
>>> client.tls_set(ca_certs="mosquitto.org.crt",
certfile="client.crt",keyfile="client.key")
```
## Hardware 

## Android Application

The group has decided to develop an Android application for the purposes of user interface and data displaying. The application is wrote in `JavaScript` using Android Studio.

The software uses `Paho Android Service` which is an interface to the Paho Java MQTT Client Library for the Android Platform. The MQTT connection is encapsulated within an Android-Service that runs in the background of the Android application, keeping it alive when the Android application is switching between different Activities. This layer of abstraction is needed to be able to receive MQTT messages reliably. More information about paho android service can be found at [MQTT Client Library Encyclopedia – Paho Android Service](https://www.hivemq.com/blog/mqtt-client-library-enyclopedia-paho-android-service/)

## MQTT Connection

### TLS and SSL

In our hyper-connected world, security is very important. In every IoT application, you need to consider security from the start. We have decided to use TLS and SSL to secure the data being transmitted. Transport Layer Security (TLS) and Secure Sockets Layer (SSL) provide a secure communication channel between a client and a server. 

When connecting with SSL/TLS the MQTT-broker has to use a valid certificate that is trusted via the chain of trust of the Android device or provide a custom Java SocketFactory. We use a utility class to generate an SSLSocketFactory instance specifying the BKS format certificate to trust.

```sh
options.setSocketFactory(client.getSSLSocketFactory(input, "***********"));
```

### Establish Connection 

The Paho Android Service encapsulates the MQTT connection and offers an API for that. The MQTT-connection is created and established using `client = new MqttAndroidClient(MainActivity.this, MQTTHOST, clientId);` followed by 

```sh
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
```

## Subscribe

Subscriptions can be created via the `MqttAndroidClient.subscribe` method, which takes the topic and the QOS as parameters and returns a `IMqttToken`. The token can be used to keep track if the subscription can successfully established or failed.

```sh
private void setSubscription(){
        try{
            client.subscribe(TOPIC1,1);
            client.subscribe(TOPIC2,1);
            client.subscribe(TOPIC3,1);

        }catch(MqttException e){
            e.printStackTrace();
        }
    }
```
where TOPIC1, TOPIC 2, TOPIC 3 are previously defined.

The messages are then being collected everytime the `Call back functions` are being called. Depending on the topic, different messages recieved will be stored in different arraylist. For example when `Temperature` receives an update,

```sh
TemData.add(new String(message.getPayload()));
```

The data are stored for useful purposes such as user past data and activity tracking which will be added to the applciation shortly.

## Connect and Disconnect

We have established `conn` and `disconn` just to make the application more flexible as security comes at a cost in terms of CPU usage and communication overhead. We dont want the MQTT-connection to be running at background all the time.

```sh
Conn:
IMqttToken token = client.connect(options);

Disconn:
IMqttToken token = client.disconnect();
```


## Contribution

This is the project created for Imperial College London EEE third year module Embedded System. Any external pull is not allowed.

## Aurthors

Zhenyu Luo zl4716@ic.ac.uk

Yiwen  Zou yz6316@ic.ac.uk

Rymon  Yu  rymonyu@gmail.com
