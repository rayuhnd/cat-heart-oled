from machine import Pin, I2C # type: ignore
import framebuf # type: ignore

# SH1107 driver
class SH1107:
    def __init__(self, width=128, height=128, i2c=None, addr=0x3C, flip=False):
        self.width = width
        self.height = height
        self.pages = height // 8
        self.addr = addr
        self.i2c = i2c
        self.buffer = bytearray(self.pages * width)
        self.framebuf = framebuf.FrameBuffer(self.buffer, width, height, framebuf.MONO_VLSB)
        
        # Init commands for 128x128 SH1107
        self.init_cmds = bytes([
            0xAE,       # Display OFF
            0x02,       # Lower column address
            0x10,       # Higher column address
            0xB0,       # Page address
            0xDC, 0x00, # Display start line
            0x81, 0x80, # Contrast control (adjustable)
            0xA0,       # Segment remap (normal)
            0xC0,       # COM output scan direction (normal)
            0xA6,       # Normal display (not inverted)
            0xA8, 0x7F, # Multiplex ratio (128 rows)
            0xD3, 0x60, # Display offset
            0xD5, 0x51, # Display clock divide ratio/oscillator frequency
            0xD9, 0x22, # Pre-charge period
            0xDA, 0x12, # COM pins hardware configuration
            0xDB, 0x35, # VCOMH deselect level
            0x40,       # Display start line
            0xA4,       # Entire display ON (follow RAM)
            0xA6,       # Normal display (not inverted)
            0xAF        # Display ON
        ])
        
        if flip:  # Flip the display if requested
            self.init_cmds = bytes([
                0xAE, 0x02, 0x10, 0xB0, 0xDC, 0x00, 0x81, 0x80,
                0xA1,  # Segment remap (flipped horizontally)
                0xC8,  # COM output scan direction (flipped vertically)
                0xA6, 0xA8, 0x7F, 0xD3, 0x60, 0xD5, 0x51,
                0xD9, 0x22, 0xDA, 0x12, 0xDB, 0x35,
                0x40, 0xA4, 0xA6, 0xAF
            ])
        
        # Send initialization commands
        for cmd in self.init_cmds:
            self.write_cmd(cmd)
        
        self.fill(0)
        self.show()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes([0x00, cmd]))

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b'\x40' + buf)

    def fill(self, color):
        self.framebuf.fill(color)

    def text(self, text, x, y, color=1):
        self.framebuf.text(text, x, y, color)

    def show(self):
        for page in range(self.pages):
            self.write_cmd(0xB0 | page)  # Set page address
            self.write_cmd(0x02)         # Lower column address
            self.write_cmd(0x10)         # Higher column address
            self.write_data(self.buffer[page * self.width:(page + 1) * self.width])

# Hardware setup
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
oled = SH1107(128, 128, i2c)  # Initialize display

# Main
def main():
    # Initial display test
    oled.fill(0)
    oled.text(f" /\_/\ ", -1, 30, 1)
    oled.text(f"( o.o )", -1, 40, 1)
    oled.text(f" > ^ <", -1, 50, 1)
    oled.text(f" Hello", -1, 60, 1)
    oled.text(f" Pook!", -1, 70, 1)
    oled.text(f"  <3   ", -1, 80, 1)
    oled.text(f" i lik u", -1, 90, 1)
    oled.show()

    
main()