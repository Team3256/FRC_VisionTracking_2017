from networktables import NetworkTables
import logging
import time

logging.basicConfig(level=logging.DEBUG)
NetworkTables.setIPAddress('roborio-3256-frc.local')
NetworkTables.setClientMode()
NetworkTables.initialize()
nt = NetworkTables.getTable('SmartDashboard')
while True:
    time.sleep(0.5)
    print nt.getNumber("gyro", 0)
