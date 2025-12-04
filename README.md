<h1 align="center">Remote Irrigation</h1>
<p align="center">
  <img src="videoframe_3483.png" width="500"/>
</p>
<p align="center">─────────────────────────────────────────────────────</p>
<p align="center"><strong>A simple, reliable, IoT irrigation platform for farmers without infrastructure overhaul</strong></p>

<p align="center">─────────────────────────────────────────────────────</p>

# Features

- 🧩 Simple user onboarding and device provisioning for tanks, valves, pumps, hubs, and edge controllers.
- ⚡ Real-time monitoring and remote control through the Android app.
- 💧 Configurable water tanks: fill, drain, idle, or simultaneous fill-and-drain modes.
- 🔐 Secure communication using HTTPS and JWT-based authentication
- 🔄 Fault-tolerant edge devices with automatic reconnection after power or network outages.

# Demonstration Video
[![Watch the video](https://img.youtube.com/vi/VIDEO_ID/hqdefault.jpg)](https://www.youtube.com/shorts/RhWYphY1hrE)

# Table of Contents

- Summary
- Architecture
- details
- File paths
# Summary

**Key Highlights**
- Real microcontroller hardwares.
- Real-time actuation <3s latency tested nationwide.
- Survives power/Wi-Fi outages (auto reconnect + state recovery).
- Secure end-to-end: HTTPS, JWT, MQTT over TLS with private CA.

**Remote Irrigation** is an IoT platform that turns any normal water tank, valve, pump on a farm into a smart, internet-controllable asset. Users create accounts, provision physical devices (valves, pumps, level sensors) in seconds, and monitor/actuate everything live from an Android app — including simultaneous fill + drain operations. Edge nodes automatically survive multi-day Wi-Fi and power outages. Every connection is protected via JWT + TLS. Uses Async FastAPI + Async MQTT pipeline, < 3s real-time latency for all actuation operations, from anywhere in South Korea to any farm in South Korea. and tested on real hardwares for connection reliability.
All firmware, backend, frontend, is built from scratch, and the server is live on Ubuntu VM on cloud, ready for users.

# Architecture
<p align="center">
  <img src=Untitled Diagram-Page-1.drawio.png width="500"/>
</p>
