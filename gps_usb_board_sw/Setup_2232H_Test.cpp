//
// SPITEST.cpp : VC++ console application.
// this example project use port A of FT2232H to access SPI EEPROM 93C56
// we send 16 word data to 93C56 and read them back, user can see the test
// result in command mode.
//#include "stdafx.h"
//#include <windows.h>
#include "ftd2xx.h"
#include "max2769.h"
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
//declare parameters for 93C56
#define MemSize 16 //define data quantity you want to send out
const BYTE SPIDATALENGTH = 11;//3 digit command + 8 digit address
const BYTE READ = '\xC0';//110xxxxx
const BYTE WRITE = '\xA0';//101xxxxx
const BYTE WREN = '\x98';//10011xxx
const BYTE ERAL = '\x90';//10010xxx
//declare for BAD command
const BYTE AA_ECHO_CMD_1 = '\xAA';
const BYTE AB_ECHO_CMD_2 = '\xAB';
const BYTE BAD_COMMAND_RESPONSE = '\xFA';
//declare for MPSSE command
//const BYTE MSB_RISING_EDGE_CLOCK_BYTE_OUT = '\x10';
const BYTE MSB_FALLING_EDGE_CLOCK_BYTE_OUT = '\x11';
//const BYTE MSB_RISING_EDGE_CLOCK_BIT_OUT = '\x12';
//const BYTE MSB_FALLING_EDGE_CLOCK_BIT_OUT = '\x13';
//const BYTE MSB_RISING_EDGE_CLOCK_BYTE_IN = '\x20';
//const BYTE MSB_RISING_EDGE_CLOCK_BIT_IN = '\x22';
//const BYTE MSB_FALLING_EDGE_CLOCK_BYTE_IN = '\x24';
//const BYTE MSB_FALLING_EDGE_CLOCK_BIT_IN = '\x26';
FT_STATUS ftStatus; //Status defined in D2XX to indicate operation result
BYTE OutputBuffer[512]; //Buffer to hold MPSSE commands and data to be sent to FT2232H
BYTE InputBuffer[512]; //Buffer to hold Data bytes to be read from FT2232H
DWORD dwClockDivisor = 29; //Value of clock divisor, SCL Frequency = 60/((1+29)*2) (MHz) = 1Mhz
DWORD dwNumBytesToSend = 0; //Index of output buffer
DWORD dwNumBytesSent = 0, dwNumBytesRead = 0, dwNumInputBuffer = 0;

BYTE ByteDataRead;
WORD MemAddress = 0x00;
WORD i=0;
WORD DataOutBuffer[MemSize];
WORD DataInBuffer[MemSize];

//this routine is used to enable SPI device
void SPI_CSEnable()
{
    for(int loop=0;loop<5;loop++) //one 0x80 command can keep 0.2us, do 5 times to stay in this situation for 1us 
    {
        OutputBuffer[dwNumBytesToSend++] = '\x80';//GPIO command for ADBUS
        OutputBuffer[dwNumBytesToSend++] = '\x00';//set CS lo, MOSI lo and SCL lo
        OutputBuffer[dwNumBytesToSend++] = '\x0b';//bit3:CS, bit2:MISO, bit1:MOSI, bit0:SCK
    }
}

//this routine is used to disable SPI device
void SPI_CSDisable()
{
    for(int loop=0;loop<5;loop++) //one 0x80 command can keep 0.2us, do 5 times to stay in this situation for 1us
    {
        OutputBuffer[dwNumBytesToSend++] = '\x80';//GPIO command for ADBUS
        OutputBuffer[dwNumBytesToSend++] = '\x08';//set CS hi, MOSI lo and SCL lo
        OutputBuffer[dwNumBytesToSend++] = '\x0b';//bit3:CS, bit2:MISO, bit1:MOSI, bit0:SCK
    }
}


//this routine is used to initial SPI interface
BOOL SPI_Initial(FT_HANDLE ftHandle)
{
    // "Configure FTDI Port For MPSSE Use"
    DWORD dwCount;
    ftStatus = FT_ResetDevice(ftHandle); //Reset USB device
    //Purge USB receive buffer first by reading out all old data from FT2232H receive buffer
    ftStatus |= FT_GetQueueStatus(ftHandle, &dwNumInputBuffer); // Get the number of bytes in the FT2232H receive buffer
    if ((ftStatus == FT_OK) && (dwNumInputBuffer > 0))
        ftStatus |= FT_Read(ftHandle, InputBuffer, dwNumInputBuffer, &dwNumBytesRead); //Read out the data from FT2232H receive buffer
    ftStatus |= FT_SetUSBParameters(ftHandle, 65535, 65535); //Set USB request transfer size
    ftStatus |= FT_SetChars(ftHandle, false, 0, false, 0); //Disable event and error characters
    ftStatus |= FT_SetTimeouts(ftHandle, 3000, 3000); //Sets the read and write timeouts in 3 sec for the FT2232H
    ftStatus |= FT_SetLatencyTimer(ftHandle, 1); //Set the latency timer
    ftStatus |= FT_SetBitMode(ftHandle, 0x0, 0x00); //Reset controller
    ftStatus |= FT_SetBitMode(ftHandle, 0x0, 0x02); //Enable MPSSE mode
    if (ftStatus != FT_OK)
    {
        printf("fail on initialize FT2232H device ! \n");
        return false;
    }
    sleep(1); // Wait 1s for all the USB stuff to complete and work
    //////////////////////////////////////////////////////////////////
    // Synchronize the MPSSE interface by sending bad command &xAA*
    //////////////////////////////////////////////////////////////////

    dwNumBytesToSend = 0;
    OutputBuffer[dwNumBytesToSend++] = '\xAA'; //Add BAD command &xAA*
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent); // Send off the BAD commands
    dwNumBytesToSend = 0; //Clear output buffer
    do{
        ftStatus = FT_GetQueueStatus(ftHandle, &dwNumInputBuffer); // Get the number of bytes in the device input buffer
    }while ((dwNumInputBuffer == 0) && (ftStatus == FT_OK)); //or Timeout
    bool bCommandEchod = false;
    ftStatus = FT_Read(ftHandle, InputBuffer, dwNumInputBuffer, &dwNumBytesRead); //Read out the data from input buffer
    for (dwCount = 0; dwCount < (dwNumBytesRead - 1); dwCount++) //Check if Bad command and echo command received
    {
        if ((InputBuffer[dwCount] == BYTE('\xFA')) && (InputBuffer[dwCount+1] == BYTE('\xAA')))
        {
            bCommandEchod = true;
            break;
        }
    }
    if (bCommandEchod == false)
    {
        printf("fail to synchronize MPSSE with command '0xAA' \n");
        return false; /*Error, can*t receive echo command , fail to synchronize MPSSE interface;*/
    }
    //////////////////////////////////////////////////////////////////
    // Synchronize the MPSSE interface by sending bad command &xAB*
    //////////////////////////////////////////////////////////////////
    //dwNumBytesToSend = 0; //Clear output buffer
    OutputBuffer[dwNumBytesToSend++] = '\xAB'; //Send BAD command &xAB*
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent); // Send off the BAD commands
    dwNumBytesToSend = 0; //Clear output buffer
    do{
        ftStatus = FT_GetQueueStatus(ftHandle, &dwNumInputBuffer); //Get the number of bytes in the device input buffer
    }while ((dwNumInputBuffer == 0) && (ftStatus == FT_OK)); //or Timeout
    bCommandEchod = false;

    ftStatus = FT_Read(ftHandle, InputBuffer, dwNumInputBuffer, &dwNumBytesRead); //Read out the data from input buffer
    for (dwCount = 0;dwCount < (dwNumBytesRead - 1); dwCount++) //Check if Bad command and echo command received
    {
        if ((InputBuffer[dwCount] == BYTE('\xFA')) && (InputBuffer[dwCount+1] == BYTE( '\xAB')))
        {
            bCommandEchod = true;
            break;
        }
    }
    if (bCommandEchod == false)
    {
        printf("fail to synchronize MPSSE with command '0xAB' \n");
        return false;
        /*Error, can't receive echo command , fail to synchronize MPSSE interface;*/
    }

    ////////////////////////////////////////////////////////////////////
    //Configure the MPSSE for SPI communication with MAX 2769
    //////////////////////////////////////////////////////////////////
    OutputBuffer[dwNumBytesToSend++] = '\x8A'; //Ensure disable clock divide by 5 for 60Mhz master clock
    OutputBuffer[dwNumBytesToSend++] = '\x97'; //Ensure turn off adaptive clocking
    OutputBuffer[dwNumBytesToSend++] = '\x8D'; //disable 3 phase data clock
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent); // Send out the commands
    if (ftStatus != FT_OK)
    {
        printf("fail on 1 \n");
        return false;
    }
    dwNumBytesToSend = 0; //Clear output buffer

    OutputBuffer[dwNumBytesToSend++] = '\x82'; //Command to set directions of upper 8 pins and force value on bits set as output
    OutputBuffer[dwNumBytesToSend++] = '\xff'; //Set *SHDN and *IDLE as outputs with high value
    OutputBuffer[dwNumBytesToSend++] = '\x0c'; //Set GPIO2 and GPIO3 as outputs

    OutputBuffer[dwNumBytesToSend++] = '\x80'; //Command to set directions of lower 8 pins and force value on bits set as output
    OutputBuffer[dwNumBytesToSend++] = '\x08'; //Set CS and CLK lo
    OutputBuffer[dwNumBytesToSend++] = '\x0b'; //Set CS, CLK, DO as out, DI as in

    // The SK clock frequency can be worked out by below algorithm with divide by 5 set as off
    // SK frequency = 60MHz /((1 + [(1 +0xValueH*256) OR 0xValueL])*2)
    OutputBuffer[dwNumBytesToSend++] = '\x86'; //Command to set clock divisor
    OutputBuffer[dwNumBytesToSend++] = BYTE(dwClockDivisor & '\xFF'); //Set 0xValueL of clock divisor
    OutputBuffer[dwNumBytesToSend++] = BYTE(dwClockDivisor >> 8); //Set 0xValueH of clock divisor
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent); // Send out the commands
    if (ftStatus != FT_OK)
    {
        printf("fail on 2 \n");
        return false;
    }
    dwNumBytesToSend = 0; //Clear output buffer
    sleep(1); //Delay for a while

    //Turn off loop back in case
    OutputBuffer[dwNumBytesToSend++] = '\x85'; //Command to turn off loopback of TDI/TDO connection
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent); // Send out the commands
    if (ftStatus != FT_OK)
    {
        printf("fail on 3 \n");
        return false;
    }
    dwNumBytesToSend = 0; //Clear output buffer
    sleep(10); //Delay for a while
    printf("SPI initial successful\n");
    return true;
}

BOOL SPI_WriteMAX2769Register(FT_HANDLE ftHandle, BYTE *regData) {
    dwNumBytesSent=0;
    SPI_CSEnable();
    OutputBuffer[dwNumBytesToSend++] = MSB_FALLING_EDGE_CLOCK_BYTE_OUT;
    OutputBuffer[dwNumBytesToSend++] = 3;
    OutputBuffer[dwNumBytesToSend++] = 0;//Data length of 0x0003 means 4 byte data to clock out
    OutputBuffer[dwNumBytesToSend++] = *(regData);
    OutputBuffer[dwNumBytesToSend++] = *(regData + 1);
    OutputBuffer[dwNumBytesToSend++] = *(regData + 2);
    OutputBuffer[dwNumBytesToSend++] = *(regData + 3);
    SPI_CSDisable();
    ftStatus = FT_Write(ftHandle, OutputBuffer, dwNumBytesToSend, &dwNumBytesSent);//send out MPSSE command to MPSSE engine
    if (ftStatus != FT_OK)
    {
        printf("fail on register write \n");
        return false;
    }
    dwNumBytesToSend = 0; //Clear output buffer
    return true;
}

bool InitMAX2769Config(max2769Config *config, max2769RegData *regData) {
    InitConfig_CONF1(config, regData);
    InitConfig_CONF2(config, regData);
    InitConfig_CONF3(config, regData);
    InitConfig_PLLCONF(config, regData);
    InitConfig_DIV(config, regData);
    InitConfig_FDIV(config, regData);
    InitConfig_STRM(config, regData);
    InitConfig_CLK(config, regData);
    return 1;
}

void WriteMAX2769Config(FT_HANDLE ftHandle, max2769RegData regData) {
    SPI_WriteMAX2769Register(ftHandle, regData.CONF1);
    SPI_WriteMAX2769Register(ftHandle, regData.CONF2);
    SPI_WriteMAX2769Register(ftHandle, regData.CONF3);
    SPI_WriteMAX2769Register(ftHandle, regData.PLLCONF);
    SPI_WriteMAX2769Register(ftHandle, regData.DIV);
    SPI_WriteMAX2769Register(ftHandle, regData.FDIV);
    SPI_WriteMAX2769Register(ftHandle, regData.STRM);
    SPI_WriteMAX2769Register(ftHandle, regData.CLK);
}

void ConvertSamples(UCHAR dataIn[], CHAR samplesOut[], DWORD nIn) {
    /* converting from signed mag to 2's complement:
       b0 : I0  Imag
       b1 : I1  Isign
       b2 : Q0  Qmag
       b3 : Q1  Qsign */
    // CHAR sampleI[16] = {0, 128, 1, 255, 0, 128, 1, 255, 0, 128, 1, 255, 0, 128, 1, 255};
    CHAR sampleI[16] = {42, 127, 213, 128, 42, 127, 213, 128, 42, 127, 213, 128, 42, 127, 213, 128};
    CHAR sampleQ[16] = {42, 42, 42, 42, 127, 127, 127, 127, 213, 213, 213, 213, 128, 128, 128, 128};


    for (DWORD i=0; i<nIn; i++) {
         samplesOut[2*i] = sampleI[dataIn[i] & 0x0f];
         samplesOut[2*i+1] = sampleQ[dataIn[i] & 0x0f];
    }
    return;
}

void CaptureSignalFile(FT_HANDLE ftdiHandle, FILE *pFile) {
    // Capture a fixed amount of data 
    DWORD nSamplesToCapture = 120000000; // 30 seconds @ 4MSPS
    DWORD RxBytes;
    DWORD TxBytes;
    DWORD EventDword;
    UCHAR data_in[65536]; // declare a large buffer for incoming data
    CHAR  samples[131072];
    DWORD r_data_len = RxBytes;
    DWORD data_read;
    DWORD data_written;

    DWORD nCaptured = 0;

    ftStatus = FT_GetStatus(ftdiHandle, &RxBytes, &TxBytes, &EventDword);
    while ((ftStatus == FT_OK) && (nCaptured < nSamplesToCapture)) {
        while ((ftStatus == FT_OK) && (RxBytes == 0)) {
            ftStatus = FT_GetStatus(ftdiHandle, &RxBytes, &TxBytes, &EventDword);
	}
	if (ftStatus != FT_OK) {
	    printf("Status not ok in loop!\n");
	    break;
	}
        // printf("bytes in RX queue %d\n", RxBytes);
        ftStatus = FT_Read(ftdiHandle, data_in, RxBytes, &data_read);
        if (ftStatus != FT_OK)
            printf("status not ok after FT_READ: %d\n", ftStatus);
        else {
            // printf("bytes read %d\n", data_read);
            ConvertSamples(data_in, samples, data_read);
            data_written = fwrite((void *)(samples), 1, 2*data_read, pFile);
	    if (data_written != 2*data_read) {
                printf("error, data written was %d but should be %d\n", data_written, 2*data_read);
	    }
	    nCaptured += data_read;
        }
    }
    if (ftStatus != FT_OK) 
	printf("Status not ok at loop exit!\n");
	    
}

int main(int argc, char* argv[])
{
    FT_HANDLE ftdiHandleSPI, ftdiHandleBitBang;
    DWORD numDevs;
    FT_DEVICE_LIST_INFO_NODE *devInfo;
    ftStatus = FT_CreateDeviceInfoList(&numDevs);
    if (ftStatus == FT_OK)
        printf("Number of devices is %d\n",numDevs);
    else
        return 1;
    if (numDevs > 0) {
        // allocate storage for list based on numDevs
        devInfo = (FT_DEVICE_LIST_INFO_NODE*)malloc(sizeof(FT_DEVICE_LIST_INFO_NODE)*numDevs); 
        // get the device information list
        ftStatus = FT_GetDeviceInfoList(devInfo,&numDevs);
        if (ftStatus == FT_OK) {
            for (i = 0; i < numDevs; i++) {
                printf("Dev %d:\n",i);
                printf(" Flags=0x%x\n",devInfo[i].Flags);
                printf(" Type=0x%x\n",devInfo[i].Type);
                printf(" ID=0x%x\n",devInfo[i].ID);
                printf(" LocId=0x%x\n",devInfo[i].LocId);
                printf(" SerialNumber=%s\n",devInfo[i].SerialNumber);
                printf(" Description=%s\n",devInfo[i].Description);
                printf(" ftHandle=0x%x\n",devInfo[i].ftHandle);
            }
        }
    }
    else
        return 1;
    ftStatus = FT_Open(0,&ftdiHandleSPI);
    if (ftStatus != FT_OK)
    {
        printf("Can't open FT2232H device! \n");
        return 1;
    }
    else // Port opened successfully
        printf("Successfully open FT2232H device! \n");

    if(SPI_Initial(ftdiHandleSPI) == TRUE)
    {
	max2769Config config;
	max2769RegData regData;

	printf("Initialize success!\n");

	InitMAX2769Config(&config, &regData);
	DisplayMAX2769Config(regData);
	WriteMAX2769Config(ftdiHandleSPI, regData);
        /*
	BYTE regData2[4];
	BYTE *regPtr;

	regPtr = &(regData2[0]);
        GetMAX2769_CONF1(regPtr);

	DisplayReg(regPtr);
        if (SPI_WriteMAX2769Register(ftdiHandleSPI, regPtr)) 
		printf("CONF write success!\n");
	else
		printf("CONF write failed...\n");
	*/
    }
    else {
        printf("Initialize failed...\n");
    }
    ftStatus = FT_Open(1, &ftdiHandleBitBang);    
    if (ftStatus != FT_OK)
    {
        printf("Can't open FT2232H BitBang device! \n");
        return 1;
    }
    else { // Port opened successfully
        printf("Successfully open FT2232H BitBang device! \n"); // see AN_373
 	ftStatus = FT_SetTimeouts(ftdiHandleBitBang,500,500);
        if(ftStatus != FT_OK)
            printf("timeout device status not ok %d\n", ftStatus);


        FILE* pFile;
        pFile = fopen("file.binary", "wb");

        CaptureSignalFile(ftdiHandleBitBang, pFile);
    //for (unsigned long long j = 0; j < 1024; ++j){
    //    
    //    fwrite(a, 1, size*sizeof(unsigned long long), pFile);
    //}
        fclose(pFile);
        /*
        ftStatus |= FT_SetUSBParameters(ftdiHandleBitBang, 4096, 4096);
	ftStatus |= FT_SetChars(ftdiHandleBitBang, false, 0, false, 0);
	ftStatus |= FT_SetTimeouts(ftdiHandleBitBang, 5000, 5000);
	ftStatus |= FT_SetLatencyTimer(ftdiHandleBitBang, 16);
	ftStatus |= FT_SetFlowControl(ftdiHandleBitBang, FT_FLOW_NONE, 0x11, 0x13);
	ftStatus |= FT_SetBaudRate(ftdiHandleBitBang, 62500);
	if (ftStatus != FT_OK)
	    printf("ftStatus not OK; %d\n", ftStatus);
	    printf("Press rtn to exit\n");
	    getchar();
	} else {
	    ftStatus = FT_SetBitMode(ftdiHandleBitBang, mask, mode)
    	    dwNumBytesToSend = 0; //Clear output buffer
            OutputBuffer[dwNumBytesToSend++] = '\x83'; // Read Upper GPIOs
	}
        */
    }
    
    FT_Close(ftdiHandleSPI);
    return 0;
}
