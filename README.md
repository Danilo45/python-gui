# Environment Monitoring System

This is a Python-based environment monitoring application that communicates with a microcontroller (e.g., STM32 with MS8607 sensor) to collect and visualize environmental data such as temperature and pressure. Due to hardware limitations, the humidity value is currently simulated.

> **This project is a continuation of the previous project** from the repository [`pressure-temp-pic32`](https://github.com/Danilo45/pressure-temp-pic32)  
> **Developed as part of the university course**: *Merno informacioni sistemi i smart tehnologije

## Features

- **Serial Data Collection**: Receives temperature and pressure data via serial communication (e.g., COM port) from a microcontroller. Humidity is simulated due to MS8607 limitations.
- **Qt-Based GUI**: Built with PySide6 (Qt for Python), the application features a responsive and user-friendly graphical interface.
- **Live Data Display**: Displays temperature, pressure, and humidity (simulated) with labels and progress bars.
- **Color-Coded Warnings**:
  - **Temperature** > 30 °C: red bar.
  - **Pressure** > 1020 hPa: red bar.
  - **Humidity** > 70%: red bar (simulated).
- **Live Plotting**: Matplotlib graphs for tracking values over time.
- **Serial Port Control**: Start and stop buttons for managing data communication.

## GUI Overview

- **Developed with PySide6 (Qt for Python)**
- Uses **QPlainTextEdit**, **QPushButton**, **QLabel**, and **QProgressBar** widgets.
- Embedded **matplotlib** canvas for plotting time-series data in real time.
- Color-coded indicators make it easy to spot abnormal conditions.


## Future Enhancements

- Add support for multiple sensors to collect data from various sources.
- Implement CSV or JSON data export functionality.
- Provide more complex analytics and trends over time.


