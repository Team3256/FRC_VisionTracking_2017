from networktables import NetworkTables       
import constants                                                                
import Image
import hashlib
from io import BytesIO

def get_image_hash():
    hasher = hashlib.md5()
    with open('frame.jpg', 'rb') as file:
        buff = file.read()
        hasher.update(buff)
    return hasher.hexdigest()

def main():
    NetworkTables.setIPAddress(constants.DRIVER_STATION_IP)
    NetworkTables.setClientMode()
    NetworkTables.initialize()
    table = NetworkTables.getTable('Image')
    temp_hash = None
    while True:
        #print table.isConnected()
        image_hash = get_image_hash()
        if image_hash != temp_hash:
            temp_hash = image_hash
            bytes = open('frame.jpg', 'rb').read()
            if len(bytes) == 0:
                continue
            table.putRaw('image', bytes)
            #print(str(round(float(len(bytes)) / 1024, 3)) + ' KB')

if __name__ == '__main__':
    main()
