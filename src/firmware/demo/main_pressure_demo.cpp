#include "mbed.h"
#include "Serial.h"

Ticker ps_flipper;
Serial pc(USBTX, USBRX, 9600); 
DigitalOut led(LED3);

AnalogIn ps_analogInput(PB_0);  // Use the appropriate pin for your setup

float voltage;
int ps_flag = 0;

float print_pressure(float voltage)
{
    int adcValue = static_cast<int>(voltage * 1023);
    float data = (voltage * 3.3 - 0.5)*4.5;
    data = (data/(0.0075*0.0075*3.141592))*0.007501;
    ps_flag = false;
    return data;
}

void ps_flag_flip(void)
{
    led = !led;
    ps_flag = 1;
}

int main() 
{
    float result = 0;
    ps_flipper.attach_us(&ps_flag_flip, 20000);
    
    while(1) 
    {
        pc.printf("");

        if (ps_flag > 0)
        {
            result = print_pressure(ps_analogInput.read());
            pc.printf("%f\n", result);
            ps_flag = 0;
        }
    }
}
