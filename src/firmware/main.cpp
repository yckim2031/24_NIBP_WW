#include "mbed.h"
#include "MAXM86161.h"

// Define the PPG Sensor
static BufferedSerial uart(USBTX, USBRX, 115200);

static int A_FULL = 0x1C;                                                 // Set A_FULL interrupt set when 100 new samples pushed in

int cnt = 0;
// Define I2C connection
DigitalOut ppg_enable(D9);
AnalogIn ps_analogInput(PB_0);                                             // Use the appropriate pin for your setup

I2C ppg_i2c(D0, D1);
DigitalOut led(LED1);
MAXM86161 ppg(ppg_i2c);
Ticker flipper;

bool print_flg = false;
bool main_flg = true;

// led
void flip(){
    led = !led;
    //main_flg = !main_flg;
}

int _read_from_reg(int address, int &data);

float print_pressure(float voltage)
{
    int adcValue = static_cast<int>(voltage * 1023);
    float data = (voltage * 3.3 - 0.5)*4.5;
    data = (data/(0.0075*0.0075*3.141592))*0.007501;
    return data;
}

int main()
{
    ppg_enable.write(1);
    ppg_i2c.frequency(400000);                  //I2C frequency to 400 kbits/s
    int status;                                 //I2C communication state (status = 0 success, else = fail)
    int grn[4];
    int channel_cnt = 2;
    int number_of_bytes = 4;
    char cmd[16];
    char databuffer[number_of_bytes*BYTES_PER_CH];
    char datacounter[1];

    int irq_1_data;
    int fifo_full = 0;                               //if ppg_full == 1, PPG FIFO is full
    int fifo_new = 0;
    int sample_cnt;

    ppg.init();                                     // Initialize the sensor with default values
    ppg.start();
    flipper.attach(&flip, 1000ms);

    while(main_flg){
        status = _read_from_reg(REG_IRQ_STATUS1, irq_1_data);

        fifo_full = irq_1_data&0x80;                // if new data comes in, read start
        fifo_full = fifo_full >> 7;

        if(fifo_full){
            cmd[0] = 0x07;
            status = ppg_i2c.write(PPG_ADDR, cmd, 1, true);
            status = ppg_i2c.read(PPG_ADDR, datacounter, 1);
            uint8_t data_cnt = datacounter[0];

            cnt = cnt + 1;
            cmd[0] = 0x08;
            status = ppg_i2c.write(PPG_ADDR, cmd, 1, true);
            status = ppg_i2c.read(PPG_ADDR, databuffer, number_of_bytes*BYTES_PER_CH);

            float result = print_pressure(ps_analogInput.read());                   // Pressure sensor Analog read
            
            for(int i=0; i<4; i++){
                grn[i] = databuffer[0+3*i]<<16|databuffer[1+3*i]<<8|databuffer[2+3*i];
                grn[i] = grn[i] & MASK_PPG_LABEL;
                printf("%d %f\n", grn[i], result);
            }

            // uart.write(databuffer, 32);
            fifo_full = 0;
        }
    }
    printf("collected data count: %d\n", cnt);
}

// Function to read from a registry
int _read_from_reg(int address, int &data)
{
    char cmd[16];
    char rsp[256];
    int status;
    cmd[0] = address;
    status = ppg_i2c.write(PPG_ADDR, cmd, 1, true);
    if(status !=0) {
        // serial_pc.printf("Failed to write register address %#X during read.\n", address);
        return status;
        }
    
    status = ppg_i2c.read(PPG_ADDR, rsp, 1);
    if(status !=0){        
        // serial_pc.printf("Failed to read register %#X value during read.\n", address);

        return status;
        }

    data = rsp[0];
    // serial_pc.printf("\n\r %#X Status: %#X\n\r", address, rsp[0]);
    return status;
}
