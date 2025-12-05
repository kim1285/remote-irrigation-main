
<p align="center">
  <a href="https://github.com/kim1285/remote-irrigation-main/blob/main/README_KOREAN.md"><strong>한국어도 있어요</strong></a>
</p>

<h1 align="center">Remote Irrigation</h1>
<p align="center">
  <img src="videoframe_3483.png" width="500"/>
  <br>
  <p align="center"
    
  [![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04-E95420?logo=ubuntu&logoColor=white)](https://ubuntu.com/)
  [![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![MQTT](https://img.shields.io/badge/MQTT-v5-FFC20E?logo=mqtt&logoColor=black)](https://mqtt.org/)
  [![MicroPython](https://img.shields.io/badge/MicroPython-v1.23-00A8E8?logo=python&logoColor=white)](https://micropython.org/)
  [![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-5-C51A4A?logo=raspberry-pi&logoColor=white)](https://www.raspberrypi.org/)
  [![Stars](https://img.shields.io/github/stars/kim1285/remote-irrigation-main?style=social)](https://github.com/kim1285/remote-irrigation-main/stargazers)
</p>
</p>
<p align="center">─────────</p>
<p align="center"><strong>A simple, reliable, IoT irrigation platform for farmers, without infrastructure overhaul</strong></p>
<p align="center">─────────</p>

# Remote Irrigation 🌱💧  
Real-time remote irrigation control system using ESP32 + FastAPI + MQTT



# Features

- 🧩 Simple user onboarding and device provisioning for tanks, valves, pumps, hubs, and edge controllers.
- ⚡ Real-time monitoring and remote control through the Android app.
- 💧 Configurable water tanks: fill, drain, idle, or simultaneous fill-and-drain modes.
- 🔐 Secure communication using HTTPS and JWT-based authentication
- 🔄 Fault-tolerant edge devices with automatic reconnection after power or network outages.


# Demonstration Video / Live server
<p align="center">
  <a href="https://www.youtube.com/shorts/RhWYphY1hrE" target="_blank" rel="noopener">
    <img src="Untitled video - Made with Clipchamp.gif" alt="Watch demo" width="330"/>
  </a>
  <br>
  <em>Click the image to see the demo video.</em>
</p>
<p align="center"><a href="https://remote-irrigation.duckdns.org/docs#">Live server swagger doc</a></p>


# Table of Contents

- Summary
- Architecture
- Details
- File paths

# Summary
**Remote Irrigation** is an IoT platform that turns any normal water tank, valve, pump on a farm into a smart, internet-controllable asset.

**Key Highlights**
- Real microcontroller hardwares.
- Real-time actuation <3s latency tested nationwide.
- Survives power/Wi-Fi outages (auto reconnect + state recovery).
- Secure end-to-end: HTTPS, JWT, MQTT over TLS with private CA.

Users create accounts, provision physical devices (valves, pumps, level sensors) in seconds, and monitor/actuate pump, valve tank live from an Android app — including simultaneous fill + drain operations. 

All firmware, backend, frontend, is built from scratch, and the server is **live** on Ubuntu VM on cloud, ready for users.

# Architecture
<p align="center">
  <img src="Untitled Diagram-Page-1.drawio.png" width="1500"/>
  <br>
  <em>Overall High level architecture(C2)</em>
</p>

There are three main parts:
- Edge Devices → ESP32 running MicroPython (Hub + Device Manager pattern)
- Ubuntu VM ($7/month Vultr) → FastAPI + Mosquitto + MySQL + Nginx
- Frontend → Standalone React Native Android app


## Stacks
| Component               | Choice                                       | Reason                                    |
| ----------------------- | -------------------------------------------- | ----------------------------------------- |
| Hosting                 | Vultr $7/month VM                            | Cheap, simple, reliable, static public IP |
| Reverse proxy           | Nginx + Let’s Encrypt                        | HTTPS, rate limiting                      |
| Open ports              | Only 443 (HTTPS) + 8883 (MQTT/TLS)           | Security and predictability               |
| Backend                 | FastAPI + async SQLAlchemy                   | Modern, fast, async, excellent auto docs  |
| Architecture            | Clean-ish DDD layers                         | Easy to grow, readable                    |
| Database                | MySQL                                        | Simple, good async python support         |
| Message broker          | Mosquitto MQTT                               | Async Python/MicroPython support          |
| Edge → Cloud security   | MQTT over TLS+ MQTT username/pw + private CA | Secure, lightweight, works on 500 KB RAM  |
| Client → Cloud security | JWT + HTTPS                                  | Basic auth using JWT token                |
| Deployment              | systemd services                             | auto-restart on crash                     |

# Details

## Backend 
<p align="center">
  <img src="beproof.png" width="1500"/>
  <br>
  <em>Screenshot of an example API Endpoint, and swagger docs </em>
</p>

**FastAPI** serves as the core backend application and follows a simplified Domain-Driven Design (DDD) structure with clean separation of concerns. Incoming requests are validated using **Pydantic**, then processed through the **application**, **domain**, and **infrastructure** layers asynchronously before returning responses with proper exception handling.

**MySQL** is used as the primary database, accessed asynchronously via **SQLAlchemy (async extension)**. Domain aggregate states are stored persistently here — acting as a *delayed source of truth* compared to real-time device telemetry.

**Mosquitto (MQTT)** is used as the message broker for edge-to-cloud communication due to its lightweight design, stability, and excellent support in MicroPython on ESP32 devices, even with limited memory (~500 KB).


## ERD

<p align="center">
  <img src="ERD.png" width="900"/>
  <br>
  <em>Entity Relationship Diagram</em>
</p>

This diagram represents the database schema for the Remote Irrigation app. The usual relationship is `one-to-many`.

<p align="center">
  <br>
  <img src="erd-proof.png" width="1000"/>
    <br>
    <em>SQL query on live server</em>
</p>

Result of `select * from water_tanks` SQL query on live server on VM after temporarily allowing remote access to db, and then using SSL tunneling on local dev machine.


## Frontend
<p align="center">
  <img src="frontend.png" width="1000"/>
    <br>
  <em>Wireframe > code > demo</em> 
</p>
React Native(typescript) was used to build a simple frontend and it was deployed as standalone android app that sends requests to api endpoints open on Ubuntu VM. 

## Edge device
<p align="center">
  <img src="hardware3.png" width="1000"/>
    <br>
    <em>ESP32 hardwares</em> 
</p>

**Edge devices** are ESP32 running micropython async loop with exception handling. There are two types of edge devices.
**Hub** type devices manage other **Device manager** type devices.
Each only communicates to central **Mosquitto** broker on cloud. The idea behind this decision to make connection measurement simple and clear at this moment. 
The communication between Edge devices and Mosquitto broker is **MQTT over TLS**, with private certificate authority (CA) and username/password per mqtt clients. 


## Deployment
<p align="center">
  <img src="servers.png" width="600"/>
    <br>
    <em>Screenshot of sudo systemctl status ~.service</em>   
</p>

**Domain name** of a backend is from DuckDNS. 

**The server** is hosted on Ubuntu Virtual Machine on Vultr and it costs around 7 USD a month at this moment. 
Inside, **FastAPI** app, **MySQL**, **Mosquitto** Broker are running as daemons, managed by **systemd** as services.  

**Nginx** acts as a reverse proxy. It rate limits per IP(30 r/s), handles HTTPS encryption using let's encrypt, and exposes public fixed IP with ports. Only Port 443(HTTPS), port 8883(MQTT over TLS) is open due to safely.


# Backend File paths
```
backend/
└── src/
    ├── api/
    │   └── v1/
    │       ├── mappers/
    │       │   └── provision.py
    │       └── routes/
    │           ├── auth.py
    │           ├── farms.py
    │           ├── health.py
    │           ├── pre_tanks.py
    │           ├── provision.py
    │           ├── pulsecheck_route.py
    │           ├── users.py
    │           ├── valves.py
    │           ├── water_pumps.py
    │           └── water_tanks.py
    ├── application/
    │   ├── services/
    │   │   ├── app_status_service.py
    │   │   ├── check_admin_service.py
    │   │   ├── client_service.py
    │   │   ├── http_bearer_service.py
    │   │   ├── mqtt_tls_service.py
    │   │   ├── mqtt_topic_manager_service.py
    │   │   ├── password_service.py
    │   │   ├── ProvisionService.py
    │   │   ├── pump_app_service.py
    │   │   ├── token_service.py
    │   │   ├── valve_app_service.py
    │   │   └── water_tank_application_service.py
    │   ├── auth_usecase.py
    │   ├── ESP32DeviceManagerUseCase.py
    │   ├── ESP32HubUseCase.py
    │   ├── GetUserDevicesIdListUseCase.py
    │   ├── LoginUseCase.py
    │   ├── PreWaterTankUseCase.py
    │   ├── ProvisionUseCase.py
    │   ├── UserUseCase.py
    │   ├── ValveUseCase.py
    │   ├── WaterPumpUseCase.py
    │   └── WaterTankUseCase.py
    ├── domain/
    │   ├── interfaces/
    │   │   ├── mqtt/
    │   │   │   └── water_tank_reader.py
    │   │   ├── esp32_device_manager_repo.py
    │   │   ├── esp32_hub_repo.py
    │   │   ├── password_service_repo.py
    │   │   ├── pre_water_tank_repo.py
    │   │   ├── user_repo.py
    │   │   ├── valve_repo.py
    │   │   ├── water_pump_repo.py
    │   │   └── water_tank_repo.py
    │   ├── model/
    │   │   ├── esp32_device_manager.py
    │   │   ├── esp32_hub.py
    │   │   ├── pre_water_tank.py
    │   │   ├── user.py
    │   │   ├── valve.py
    │   │   ├── water_pump.py
    │   │   └── water_tank.py
    │   ├── services/
    │   │   └── water_tank_domain_service.py
    │   ├── value_objects/
    │   │   ├── datatypes.py
    │   │   ├── password.py
    │   │   └── user_devices_id_list.py
    │   └── Exceptions.py
    ├── infrastructure/
    │   ├── db/
    │   │   ├── db_async/
    │   │   │   └── session.py
    │   │   ├── mappers/
    │   │   │   ├── esp32_device_manager_mapper.py
    │   │   │   ├── esp32_hub_mapper.py
    │   │   │   ├── pre_water_tank_mapper.py
    │   │   │   ├── user_mapper.py
    │   │   │   ├── valve_mapper.py
    │   │   │   ├── water_pump_mapper.py
    │   │   │   └── water_tank_mapper.py
    │   │   ├── models/
    │   │   │   ├── esp32_device_manager.py
    │   │   │   ├── esp32_hub.py
    │   │   │   ├── pre_water_tank.py
    │   │   │   ├── user.py
    │   │   │   ├── valve.py
    │   │   │   ├── water_pump.py
    │   │   │   └── water_tank.py
    │   │   ├── repository/
    │   │   │   ├── sqlalchemy_esp32_device_manager_repository.py
    │   │   │   ├── sqlalchemy_esp32_repository.py
    │   │   │   ├── sqlalchemy_pre_water_tank_repository.py
    │   │   │   ├── sqlalchemy_user_repository.py
    │   │   │   ├── sqlalchemy_valve_repository.py
    │   │   │   ├── sqlalchemy_water_pump_repository.py
    │   │   │   └── sqlalchemy_water_tank_repository.py
    │   │   ├── base.py
    │   │   └── create_tables.py
    │   ├── mqtt/
    │   │   ├── app_status.py
    │   │   ├── mesage_router.py
    │   │   ├── mqtt_client.py
    │   │   ├── mqtt_message_handlers.py
    │   │   └── mqtt_publisher.py
    │   └── security/
    │       ├── pw_hasher.py
    │       ├── random_key_generator.py
    │       └── token_service.py
    ├── schemas/
    │   ├── dto/
    │   │   ├── auth.py
    │   │   ├── pre_tank.py
    │   │   ├── provision.py
    │   │   ├── users.py
    │   │   ├── valve.py
    │   │   ├── water_pump.py
    │   │   ├── water_tank.py
    │   │   └── water_tank_control.py
    │   └── http/
    │       └── v1/
    │           ├── login.py
    │           ├── pre_tanks.py
    │           ├── provision.py
    │           ├── pulsecheck.py
    │           ├── users.py
    │           ├── valves.py
    │           ├── water_pumps.py
    │           └── water_tanks.py
    └── tests/
        └── unit/
            ├── application/
            │   ├── LoginUseCase.py
            │   └── mqtt_water_tank_reader.py
            └── infrastructure/
                └── db/
                    ├── sqlalchemy_user_repository.py
                    └── sqlalchemy_valve_repository.py
    main.py
```
Thanks for reading!

### Contact me
Email: rlarkdtks8713@gmail.com







