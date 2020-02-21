//
// max2769.cpp
//
// Defines configuration register format for Maxim max2769

#include "ftd2xx.h"
#include "max2769.h"
#include <stdio.h>


void InitConfig_CONF1(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->CONF1.LNAMODE.value = 0x01; // LNA2 active, LNA1 off
	config->CONF1.FCEN.value = 0x000000; // center freq = 0MHz ??
	config->CONF1.FCENX.value = 0x00; // set filter to lowpass
	// Convert config data to register bits.
	SetBits_CONF1(config, regData);
	return;
};

void InitConfig_CONF2(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->CONF2.IQEN.value = 0x01; // Enable both I and Q channels
	config->CONF2.AGCMODE.value = 0x01; // Lock I and Q channel AGC
	// Convert config data to register bits.
	SetBits_CONF2(config, regData);
	return;
};


void InitConfig_CONF3(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->CONF3.PGAQEN.value = 0x01; // Enable PGA in Q channel
	// Convert config data to register bits.
	SetBits_CONF3(config, regData);
	return;
};


void InitConfig_PLLCONF(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->PLLCONF.REFDIV.value = 0x01; // 1/4 of clock rate
	
	// Convert config data to register bits.
	SetBits_PLLCONF(config, regData);
	return;
};


void InitConfig_DIV(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->DIV.NDIV.value = 0x0181; // 385d
	config->DIV.RDIV.value = 0x0004; // sets IF to zero
	
	// Convert config data to register bits.
	SetBits_DIV(config, regData);
	return;
};


void InitConfig_FDIV(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	
	// Convert config data to register bits.
	SetBits_FDIV(config, regData);
	return;
};


void InitConfig_STRM(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	
	// Convert config data to register bits.
	SetBits_STRM(config, regData);
	return;
};


void InitConfig_CLK(max2769Config *config, max2769RegData *regData) {
	
	// Make changes to default fields.
	config->CLK.L_CNT.value = 0x001f; // 
	config->CLK.M_CNT.value = 0x0f9f; // 3999d for ADC rate = 3964125Hz
	//config->CLK.FCLKIN.value = 0x01; // Enable fractional clock divider
	// Convert config data to register bits.
	SetBits_CLK(config, regData);
	return;
};

/*
void Config_CONF1(BYTE *regPtr) {
	regCONF1 regDat;

	// Make changes to default fields.
	regDat.ANTEN.value = '\x00';
	// Convert config data to register bits.
	SetBits_CONF1(regPtr, &regDat);
	return;
};
*/

void SetBits_CONF1(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x00;
	regData->CONF1[3] |= addr;

	SetRegisterData(config->CONF1.CHIPEN,
			regData->CONF1);
	SetRegisterData(config->CONF1.IDLE,
			regData->CONF1);
	SetRegisterData(config->CONF1.ILNA1,
			regData->CONF1);
	SetRegisterData(config->CONF1.ILNA2,
			regData->CONF1);
	SetRegisterData(config->CONF1.ILO,
			regData->CONF1);
	SetRegisterData(config->CONF1.IMIX,
			regData->CONF1);
	SetRegisterData(config->CONF1.MIXPOLE,
			regData->CONF1);
	SetRegisterData(config->CONF1.LNAMODE,
			regData->CONF1);
	SetRegisterData(config->CONF1.MIXEN,
			regData->CONF1);
	SetRegisterData(config->CONF1.ANTEN,
			regData->CONF1);
	SetRegisterData(config->CONF1.FCEN,
			regData->CONF1);
	SetRegisterData(config->CONF1.FBW,
			regData->CONF1);
	SetRegisterData(config->CONF1.F3OR5,
			regData->CONF1);
	SetRegisterData(config->CONF1.FCENX,
			regData->CONF1);
	SetRegisterData(config->CONF1.FGAIN,
			regData->CONF1);
	return;
}

void SetBits_CONF2(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x01;
	regData->CONF2[3] |= addr;

	SetRegisterData(config->CONF2.IQEN,
			regData->CONF2);
	SetRegisterData16(config->CONF2.GAINREF,
			regData->CONF2);
	SetRegisterData(config->CONF2.AGCMODE,
			regData->CONF2);
	SetRegisterData(config->CONF2.FORMAT,
			regData->CONF2);
	SetRegisterData(config->CONF2.BITS,
			regData->CONF2);
	SetRegisterData(config->CONF2.DRVCFG,
			regData->CONF2);
	SetRegisterData(config->CONF2.LOEN,
			regData->CONF2);
	SetRegisterData(config->CONF2.RESERVED,
			regData->CONF2);
	SetRegisterData(config->CONF2.DIEID,
			regData->CONF2);
};

void SetBits_CONF3(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x02;
	regData->CONF3[3] |= addr;

	SetRegisterData(config->CONF3.GAININ,
			regData->CONF3);
	SetRegisterData(config->CONF3.FSLOWEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.HILOADEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.ADCEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.DRVEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.FOFSTEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.FILTEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.FHIPEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.RESERVED,
			regData->CONF3);
	SetRegisterData(config->CONF3.PGAIEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.PGAQEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMSTART,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMSTOP,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMCOUNT,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMBITS,
			regData->CONF3);
	SetRegisterData(config->CONF3.STAMPEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.TIMESYNCEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.DATSYNCEN,
			regData->CONF3);
	SetRegisterData(config->CONF3.STRMRST,
			regData->CONF3);
};

void SetBits_PLLCONF(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x03;
	regData->PLLCONF[3] |= addr;

	SetRegisterData(config->PLLCONF.VCOEN,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.IVCO,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.REFOUTEN,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.RESERVED,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.REFDIV,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.IXTAL,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.XTALCAP,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.LDMUX,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.ICP,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.PFDEN,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.CPTEST,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.INT_PLL,
			regData->PLLCONF);
	SetRegisterData(config->PLLCONF.PWRSAV,
			regData->PLLCONF);
};

void SetBits_DIV(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x04;
	regData->DIV[3] |= addr;

	SetRegisterData16(config->DIV.NDIV,
			regData->DIV);
	SetRegisterData16(config->DIV.RDIV,
			regData->DIV);
};

void SetBits_FDIV(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x05;
	regData->FDIV[3] |= addr;

	SetRegisterData32(config->FDIV.FDIV,
			regData->FDIV);
};

void SetBits_STRM(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x06;
	regData->STRM[3] |= addr;

	SetRegisterData32(config->STRM.FRAMECOUNT,
			regData->STRM);
};

void SetBits_CLK(max2769Config *config, max2769RegData *regData) {
	BYTE addr = 0x07;
	regData->CLK[3] |= addr;

	SetRegisterData16(config->CLK.L_CNT,
			regData->CLK);
	SetRegisterData16(config->CLK.M_CNT,
			regData->CLK);
	SetRegisterData(config->CLK.FCLKIN,
			regData->CLK);
	SetRegisterData(config->CLK.ADCCLK,
			regData->CLK);
	SetRegisterData(config->CLK.SERCLK,
			regData->CLK);
	SetRegisterData(config->CLK.MODE,
			regData->CLK);
};

/*
 *
void SetBits_CONF1(BYTE *regPtr, regCONF1 *regDat) {
	SetRegisterData(regDat->CHIPEN,
			regPtr);
	SetRegisterData(regDat->IDLE,
			regPtr);
	SetRegisterData(regDat->ILNA1,
			regPtr);
	SetRegisterData(regDat->ILNA2,
			regPtr);
	SetRegisterData(regDat->ILO,
			regPtr);
	SetRegisterData(regDat->IMIX,
			regPtr);
	SetRegisterData(regDat->MIXPOLE,
			regPtr);
	SetRegisterData(regDat->LNAMODE,
			regPtr);
	SetRegisterData(regDat->MIXEN,
			regPtr);
	SetRegisterData(regDat->ANTEN,
			regPtr);
	SetRegisterData(regDat->FCEN,
			regPtr);
	SetRegisterData(regDat->FBW,
			regPtr);
	SetRegisterData(regDat->F3OR5,
			regPtr);
	SetRegisterData(regDat->FCENX,
			regPtr);
	SetRegisterData(regDat->FGAIN,
			regPtr);
	return;
}

void SetBits_CONF2(BYTE *regPtr, regCONF2 *regDat) {
	SetRegisterData(regDat->IQEN,
			regPtr);
	SetRegisterData16(regDat->GAINREF,
			regPtr);
	SetRegisterData(regDat->AGCMODE,
			regPtr);
	SetRegisterData(regDat->FORMAT,
			regPtr);
	SetRegisterData(regDat->BITS,
			regPtr);
	SetRegisterData(regDat->DRVCFG,
			regPtr);
	SetRegisterData(regDat->LOEN,
			regPtr);
	SetRegisterData(regDat->RESERVED,
			regPtr);
	SetRegisterData(regDat->DIEID,
			regPtr);
};

void SetBits_CONF3(BYTE *regPtr, regCONF3 *regDat) {
	SetRegisterData(regDat->GAININ,
			regPtr);
	SetRegisterData(regDat->FSLOWEN,
			regPtr);
	SetRegisterData(regDat->HILOADEN,
			regPtr);
	SetRegisterData(regDat->ADCEN,
			regPtr);
	SetRegisterData(regDat->DRVEN,
			regPtr);
	SetRegisterData(regDat->FOFSTEN,
			regPtr);
	SetRegisterData(regDat->FILTEN,
			regPtr);
	SetRegisterData(regDat->FHIPEN,
			regPtr);
	SetRegisterData(regDat->RESERVED,
			regPtr);
	SetRegisterData(regDat->PGAIEN,
			regPtr);
	SetRegisterData(regDat->PGAQEN,
			regPtr);
	SetRegisterData(regDat->STRMEN,
			regPtr);
	SetRegisterData(regDat->STRMSTART,
			regPtr);
	SetRegisterData(regDat->STRMSTOP,
			regPtr);
	SetRegisterData(regDat->STRMCOUNT,
			regPtr);
	SetRegisterData(regDat->STRMBITS,
			regPtr);
	SetRegisterData(regDat->STAMPEN,
			regPtr);
	SetRegisterData(regDat->TIMESYNCEN,
			regPtr);
	SetRegisterData(regDat->DATSYNCEN,
			regPtr);
	SetRegisterData(regDat->STRMRST,
			regPtr);
};

void SetBits_PLLCONF(BYTE *regPtr, regPLLCONF *regDat) {
	SetRegisterData(regDat->VCOEN,
			regPtr);
	SetRegisterData(regDat->IVCO,
			regPtr);
	SetRegisterData(regDat->REFOUTEN,
			regPtr);
	SetRegisterData(regDat->RESERVED,
			regPtr);
	SetRegisterData(regDat->REFDIV,
			regPtr);
	SetRegisterData(regDat->IXTAL,
			regPtr);
	SetRegisterData(regDat->XTALCAP,
			regPtr);
	SetRegisterData(regDat->LDMUX,
			regPtr);
	SetRegisterData(regDat->ICP,
			regPtr);
	SetRegisterData(regDat->PFDEN,
			regPtr);
	SetRegisterData(regDat->CPTEST,
			regPtr);
	SetRegisterData(regDat->INT_PLL,
			regPtr);
	SetRegisterData(regDat->PWRSAV,
			regPtr);
};

void SetBits_DIV(BYTE *regPtr, regDIV *regDat) {
	SetRegisterData16(regDat->NDIV,
			regPtr);
	SetRegisterData16(regDat->RDIV,
			regPtr);
};

void SetBits_FDIV(BYTE *regPtr, regFDIV *regDat) {
	SetRegisterData32(regDat->FDIV,
			regPtr);
};

void SetBits_STRM(BYTE *regPtr, regSTRM *regDat) {
	SetRegisterData32(regDat->FRAMECOUNT,
			regPtr);
};

void SetBits_CLK(BYTE *regPtr, regCLK *regDat) {
	SetRegisterData16(regDat->L_CNT,
			regPtr);
	SetRegisterData16(regDat->M_CNT,
			regPtr);
	SetRegisterData(regDat->FCLKIN,
			regPtr);
	SetRegisterData(regDat->ADCCLK,
			regPtr);
	SetRegisterData(regDat->SERCLK,
			regPtr);
	SetRegisterData(regDat->MODE,
			regPtr);
};

*/

void GetMAX2769_CONF1(BYTE *regPtr) {

	regCONF1 regDat;
	/*
	struct max2769_CONF1 {
		const BYTE REG_ADDR = '\x00'; //xxxx0000
		// fields
		const BYTE CHIPEN = '\x01;   //xxxxxxx1
		const BYTE IDLE = '\x00;     //xxxxxxx0
		const BYTE ILNA1 = '\x08;    //xxxx1000
		const BYTE ILNA2 = '\x02;    //xxxxxx10
		const BYTE ILO = '\x02;      //xxxxxx10
		const BYTE IMIX = '\x01;     //xxxxxx01
		const BYTE MIXPOLE = '\x00;  //xxxxxxx0
		const BYTE LNAMODE = '\x00;  //xxxxxx00
		const BYTE MIXEN = '\x01;    //xxxxxxx1
		const BYTE ANTEN = '\x01;    //xxxxxxx1
		const BYTE FCEN = '\x0d;     //xx001101
		const BYTE FBW = '\x00;      //xxxxxx00
		const BYTE F3OR5 = '\x00;    //xxxxxxx0
		const BYTE FCENX = '\x01;    //xxxxxxx1
		const BYTE FGAIN = '\x01;    //xxxxxxx1
		// field msb locations
		const BYTE CHIPEN_loc = 27;
		const BYTE IDLE_loc = 26;
		const BYTE ILNA1_loc = 25;
		const BYTE ILNA2_loc = 21;
		const BYTE ILO_loc = 19;
		const BYTE IMIX_loc = 17;
		const BYTE MIXPOLE_loc = 15;
		const BYTE LNAMODE_loc = 14;
		const BYTE MIXEN_loc = 12;
		const BYTE ANTEN_loc = 11;
		const BYTE FCEN_loc = 10;
		const BYTE FBW_loc = 4;
		const BYTE F3OR5_loc = 2;
		const BYTE FCENX_loc = 1;
		const BYTE FGAIN_loc = 0;
		// field bit widths
		const BYTE CHIPEN_width = 1;
		const BYTE IDLE_width = 1;
		const BYTE ILNA1_width = 4;
		const BYTE ILNA2_width = 2;
		const BYTE ILO_width = 2;
		const BYTE IMIX_width = 2;
		const BYTE MIXPOLE_width = 1;
		const BYTE LNAMODE_width = 2;
		const BYTE MIXEN_width = 1;
		const BYTE ANTEN_width = 1;
		const BYTE FCEN_width = 6;
		const BYTE FBW_width = 2;
		const BYTE F3OR5_width = 1;
		const BYTE FCENX_width = 1;
		const BYTE FGAIN_width = 1;
	} regDat;
	*/
	// Make any changes to default fields.
	regDat.ANTEN.value = '\x00';

	// Set the data fields.
	*(regPtr + 0) = 0;
	*(regPtr + 1) = 0;
	*(regPtr + 2) = 0;
	*(regPtr + 3) = 0;
	SetRegisterData(regDat.CHIPEN,
			regPtr);
	SetRegisterData(regDat.IDLE,
			regPtr);
	SetRegisterData(regDat.ILNA1,
			regPtr);
	SetRegisterData(regDat.ILNA2,
			regPtr);
	SetRegisterData(regDat.ILO,
			regPtr);
	SetRegisterData(regDat.IMIX,
			regPtr);
	SetRegisterData(regDat.MIXPOLE,
			regPtr);
	SetRegisterData(regDat.LNAMODE,
			regPtr);
	SetRegisterData(regDat.MIXEN,
			regPtr);
	SetRegisterData(regDat.ANTEN,
			regPtr);
	SetRegisterData(regDat.FCEN,
			regPtr);
	SetRegisterData(regDat.FBW,
			regPtr);
	SetRegisterData(regDat.F3OR5,
			regPtr);
	SetRegisterData(regDat.FCENX,
			regPtr);
	SetRegisterData(regDat.FGAIN,
			regPtr);
	return;
}

void SetRegisterData(regfield field, 
		     BYTE *regDat) {

	BYTE addrOffset = 4;	
	for (BYTE i=0; i<field.width; i++) {
		BYTE bit = (field.value>>i)&'\x01';
		BYTE bitloc = field.loc - (field.width-1) + i + addrOffset;
		SetRegisterBit(bit, bitloc, regDat);
	}
}	


void SetRegisterData16(regfield16 field, 
		     BYTE *regDat) {

	BYTE addrOffset = 4;	
	for (BYTE i=0; i<field.width; i++) {
		BYTE bit = (field.value>>i)&'\x01';
		BYTE bitloc = field.loc - (field.width-1) + i + addrOffset;
		SetRegisterBit(bit, bitloc, regDat);
	}
}	


void SetRegisterData32(regfield32 field, 
		     BYTE *regDat) {

	BYTE addrOffset = 4;	
	for (BYTE i=0; i<field.width; i++) {
		BYTE bit = (field.value>>i)&'\x01';
		BYTE bitloc = field.loc - (field.width-1) + i + addrOffset;
		SetRegisterBit(bit, bitloc, regDat);
	}
}	

void SetRegisterBit(BYTE bit, BYTE loc, BYTE *regDat) {
	// regDat[0] is MSByte
	// regDat[3] is LSByte
	BYTE byteNum = 3 - (loc>>3);
	BYTE bitNum = loc&'\x07';
	
	if (bit == 1)
		regDat[byteNum] |= (bit<<bitNum); 
	else
		regDat[byteNum] &= (~(bit<<bitNum));
	return;
}

void DisplayMAX2769Config(max2769RegData regData) {
	printf("CONF1: \n");
	DisplayReg(regData.CONF1);
	printf("CONF2: \n");
	DisplayReg(regData.CONF2);
	printf("CONF3: \n");
	DisplayReg(regData.CONF3);
	printf("PLLCONF: \n");
	DisplayReg(regData.PLLCONF);
	printf("DIV: \n");
	DisplayReg(regData.DIV);
	printf("FDIV: \n");
	DisplayReg(regData.FDIV);
	printf("STRM: \n");
	DisplayReg(regData.STRM);
	printf("CLK: \n");
	DisplayReg(regData.CLK);
	printf("\n\n");
}

void DisplayReg(BYTE *regPtr) {
	for (int i=0; i<4; i++) {
		BYTE val = *(regPtr + i);
		for (int bit=7; bit>-1; bit--) {
			printf("%2d", (val>>bit)&'\x01');
		}
		printf("  ");	
	}
	printf("\n");
	return;
}
