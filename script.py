#encoding=utf-8
#for general sensor handling
from __future__ import print_function
from __future__ import division
import os
import serial  
import time
import datetime
from struct import *

#for SSD1306 graphics
import logging
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

class fb(object):
    """Base class for SSD1306-based OLED displays.  Implementors should subclass
    and provide an implementation for the _initialize function.
    """

    def __init__(self, width, height):
        self.fbdev = open("/dev/fb1", "r+b")
        self._log = logging.getLogger('Adafruit_SSD1306.SSD1306Base')
        self.width = width
        self.height = height
        self._pages = height//8
        self._buffer = [0]*(width*self._pages)

    def _initialize(self):
        raise NotImplementedError

    def display(self):
        """Write display buffer to physical display."""
        #self.fbdev.seek(0)
        #self.fbdev.write(pack("H" * len(self._buffer), self._buffer[0:128]))
        self.fbdev.seek(0)
        for byte in self._buffer:
           self.fbdev.write(pack(">B", byte))

    def image(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))

        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        index = 0
        for page in range(self._pages):
            # Iterate through all x axis columns.
            for x in range(self.width):
                # Set the bits for the column of pixels at the current position.
                bits = 0
                # Don't use range here as it's a bit slow
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= 0 if pix[(x, page*8+7-bit)] == 0 else 1
                # Update buffer byte and increment to next byte.
                self._buffer[index] = bits
                index += 1

    def image2(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))

        pix = list(image.getdata())
        step = self.width * 8
        for y in range(0, self._pages * step, step):

            buf = []
            for x in range(self.width):
                byte = 0
                for n in range(0, step, self.width):
                    byte |= (pix[x + y + n] & 0x01) << 8
                    byte >>= 1

                buf.append(byte)

            self._buffer = buf;

    def image3(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))

        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        xbytes = self.width >> 3;
        bits = 0
        for y in range(self.height):
             for x in range(self.width):
                  print('x:{} y:{} col:{}'.format(x, y, pix[(x, y)]))
                  if ((x+1) % 8):
                       bits = bits << 1;
                       bits |= 0 if pix[((x&0xf8)+(7-(x&7)), y)] == 0 else 1
                  else:
                       print('write x:{} y:{} addr:{} val:{}'.format(x, y, (x>>3) + (y*xbytes), bits))
                       self._buffer[(x>>3) + (y*xbytes)] = bits
                       bits = 0

    def image4(self, image):
        """Set buffer to value of Python Imaging Library image.  The image should
        be in 1 bit mode and a size equal to the display size.
        """
        if image.mode != '1':
            raise ValueError('Image must be in mode 1.')
        imwidth, imheight = image.size
        if imwidth != self.width or imheight != self.height:
            raise ValueError('Image must be same dimensions as display ({0}x{1}).' \
                .format(self.width, self.height))

        # Grab all the pixels from the image, faster than getpixel.
        pix = image.load()
        # Iterate through the memory pages
        xbytes = self.width >> 3;
        bits = 0
        for y in range(self.height):
           for x in range(0, self.width, 8):
               for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                  #print('x:{} y:{} col:{}'.format(x+bit, y, pix[(x+(7-bit), y)]))
	          bits = bits << 1;
	          bits |= 0 if pix[(x+(7-bit), y)] == 0 else 1
	       #print('write x:{} y:{} addr:{} val:{}'.format(x, y, (x>>3) + (y*xbytes), bits))
	       self._buffer[(x>>3) + (y*xbytes)] = bits
	       bits = 0

    def clear(self):
        """Clear contents of image buffer."""
        self._buffer = [0]*(self.width*self._pages)

#main
#create framebufer object for ssd1306
disp = fb(128, 64);
disp.clear()
width = disp.width
height = disp.height

#logo
image = Image.open("gas_mask.png").convert('1')
#disp.image4(image)
#disp.display()
#image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
# load default font.
# Alternatively load a TTF font. Make sure the .ttf font file is in the same directory as the python script!
def_font = ImageFont.truetype('small_font.ttf', 7)
#def_font = ImageFont.load_default()

# Write two lines of text.
draw.text((0, 0),  'Personal\nAir\nQuality\nSensor',  font=def_font, fill=255)
disp.image4(image)
disp.display()

print("Opening Serial Port...")
ser = serial.Serial("/dev/ttyS1", baudrate=9600, timeout=2.0)
ser_co2 = serial.Serial('/dev/ttyS2',
			baudrate=9600,
			bytesize=serial.EIGHTBITS,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			timeout=2.0)
print("Opening log file...")
log = open("polution.txt", "a")
print("Init done")

def read_co2_line(_port):
  while 1:
    result=_port.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79")
    s=_port.read(9)
    if s[0] == "\xff" and s[1] == "\x86":
      ser.flushInput()
      return ord(s[2])*256 + ord(s[3])
    break

def read_pm_line(_port):
    rv = b''
    while True:
        ch1 = _port.read()
        if ch1 == b'\x42':
            ch2 = _port.read()
            if ch2 == b'\x4d':
                rv += ch1 + ch2
                rv += _port.read(38)
                ser.flushInput()
                return rv

def main(): 
    cnt = 0
    # conn = sqlite3.connect('pm25.db')
    # c = conn.cursor()
    print("Main loop")
    while True:  

        cnt = cnt + 1
        recv = read_pm_line(ser)

	co2_value = read_co2_line(ser_co2)

	temp = open("/sys/bus/iio/devices/iio:device0/in_temp_input", "r")
	hum = open("/sys/bus/iio/devices/iio:device0/in_humidityrelative_input", "r")

        #4 first bytes is header
        tmp = recv[4:36]
        datas = unpack('>HHHHHHHHHHHHHHHH', tmp)
        header_text = (
              '\n'
              '===============================\n'
              'cnt: {} timestamp: {}\n'
              .format(cnt, datetime.datetime.now()))
        pm_text = (
              'PM1.0:  {:3d}[ug/m3]\n'
              'PM2.5:  {:3d}[ug/m3] {:.0f}[%]\n'
              'PM10:   {:3d}[ug/m3] {:.0f}[%]\n'
	      .format(datas[3], 
               datas[4], float(datas[4]) * 100.0 / 25.0, 
               datas[5], float(datas[5]) * 100.0 / 50.0))
        bucket_text = (
              '>0.3um: {}\n'
              '>0.5um: {}\n'
              '>1.0um: {}\n'
              '>2.5um: {}\n'
              '>5.0um: {}\n'
              '>10um:  {}\n'
	      .format(datas[6], datas[7], datas[8],
	       datas[9], datas[10], datas[11]))
        temp_text = (
              'co2:    {}[ppm]\n'
              'temp:   {:2.3f}[C]\n'
              'hum:    {:.2f}[%]'
              .format(co2_value,
	       float(temp.read()) / 1000.0,
	       float(hum.read())))
        long_text = header_text + pm_text + bucket_text + temp_text
        short_text = pm_text + temp_text
        print(long_text)
        print(long_text, file = log)

        draw.rectangle((0,0,width,height), outline=0, fill=0)
        draw.text((0, 0),  short_text,  font=def_font, fill=255)
        disp.image4(image)
        disp.display()

        #both temp and hum are based on industial sensor API
	temp.close()
	hum.close()
        
        #idle CPU betwen measurments
        time.sleep(0.1)  


if __name__ == '__main__':  
    try:  
        main()  
    except KeyboardInterrupt:  
        if ser != None:  
            ser.close()
        if log != None:
            log.close();

