//
// max2769.h
//
// Defines configuration register format for Maxim max2769

struct regfield {
	BYTE value;
	BYTE loc;
	BYTE width;
};

struct regfield16 {
	WORD value;
	BYTE loc;
	BYTE width;
};

struct regfield32 {
	DWORD value;
	BYTE loc;
	BYTE width;
};


struct regCONF1 {
	regfield CHIPEN = {0x01, 27, 1};
	regfield IDLE = {0x00, 26, 1};
	regfield ILNA1 = {0x08, 25, 4};
	regfield ILNA2 = {0x02, 21, 2};
	regfield ILO = {0x02, 19, 2};
	regfield IMIX = {0x01, 17, 2};
	regfield MIXPOLE = {0x00, 15, 1};
	regfield LNAMODE = {0x00, 14, 2};
	regfield MIXEN = {0x01, 12, 1};
	regfield ANTEN = {0x01, 11, 1};
	regfield FCEN = {0x0d, 10, 6};
	regfield FBW = {0x00, 4, 2};
	regfield F3OR5 = {0x00, 2, 1};
	regfield FCENX = {0x01, 1, 1};
	regfield FGAIN = {0x01, 0, 1};
};

struct regCONF2 {
	regfield IQEN = {0x00, 27, 1};
	regfield16 GAINREF = {0x0aa, 26, 12}; // 0000 1010 1010
	regfield AGCMODE = {0x00, 12, 2};
	regfield FORMAT = {0x01, 10, 2};
	regfield BITS = {0x02, 8, 3};
	regfield DRVCFG = {0x00, 5, 2};
	regfield LOEN = {0x01, 3, 1};
	regfield RESERVED = {0x00, 2, 0};
	regfield DIEID = {0x00, 1, 2};
};

struct regCONF3 {
	regfield GAININ = {0x3a, 27, 6};
	regfield FSLOWEN = {0x01, 21, 1};
	regfield HILOADEN = {0x00, 20, 1};
	regfield ADCEN = {0x01, 19, 1};
	regfield DRVEN = {0x01, 18, 1};
	regfield FOFSTEN = {0x01, 17, 1};
	regfield FILTEN = {0x01, 16, 1};
	regfield FHIPEN = {0x01, 15, 1};
	regfield RESERVED = {0x01, 14, 1};
	regfield PGAIEN = {0x01, 13, 1};
	regfield PGAQEN = {0x00, 12, 1};
	regfield STRMEN = {0x00, 11, 1};
	regfield STRMSTART = {0x00, 10, 1};
	regfield STRMSTOP = {0x00, 9, 1};
	regfield STRMCOUNT = {0x07, 8, 3};
	regfield STRMBITS = {0x01, 5, 2};
	regfield STAMPEN = {0x01, 3, 1};
	regfield TIMESYNCEN = {0x01, 2, 1};
	regfield DATSYNCEN = {0x00, 1, 1};
	regfield STRMRST = {0x00, 0, 1};
};

struct regPLLCONF {
	regfield VCOEN = {0x01, 27, 1};
	regfield IVCO = {0x00, 26, 1};
	regfield REFOUTEN = {0x01, 24, 1};
	regfield RESERVED = {0x01, 23, 1};
	regfield REFDIV = {0x03, 22, 2};
	regfield IXTAL = {0x01, 20, 2};
	regfield XTALCAP = {0x10, 18, 5};
	regfield LDMUX = {0x00, 13, 4};
	regfield ICP = {0x00, 9, 1};
	regfield PFDEN = {0x00, 8, 1};
	regfield CPTEST = {0x00, 6, 3};
	regfield INT_PLL = {0x01, 3, 1};
	regfield PWRSAV = {0x00, 2, 1};
};

struct regDIV {
	regfield16 NDIV = {0x0600, 27, 15};
	regfield16 RDIV = {0x0010, 12, 10};
};

struct regFDIV {
	regfield32 FDIV = {0x80000, 27, 20};
};

struct regSTRM {
	regfield32 FRAMECOUNT = {0x8000000, 27, 28};
};

struct regCLK {
	regfield16 L_CNT = {0x0100, 27, 12};
	regfield16 M_CNT = {0x061b, 15, 12};
	regfield FCLKIN = {0x00, 3, 1};
	regfield ADCCLK = {0x00, 2, 1};
	regfield SERCLK = {0x01, 1, 1};
	regfield MODE = {0x00, 0, 1};
};

struct regTEST1 {
	regfield32 RESERVED = {0x01e0f401, 27, 28};
};

struct regTEST2 {
	regfield32 RESERVED = {0x014c0402, 27, 28};
};

struct max2769Config {
	regCONF1 CONF1;
	regCONF2 CONF2;
	regCONF3 CONF3;
	regPLLCONF PLLCONF;
	regDIV DIV;
	regFDIV FDIV;
	regSTRM STRM;
	regCLK CLK;	
};

struct max2769RegData {
	BYTE CONF1[4] = {0, 0, 0, 0};
	BYTE CONF2[4] = {0, 0, 0, 0};
	BYTE CONF3[4] = {0, 0, 0, 0};
	BYTE PLLCONF[4] = {0, 0, 0, 0};
	BYTE DIV[4] = {0, 0, 0, 0};
	BYTE FDIV[4] = {0, 0, 0, 0};
	BYTE STRM[4] = {0, 0, 0, 0};
	BYTE CLK[4] = {0, 0, 0, 0};
};

void InitConfig_CONF1(max2769Config *config, max2769RegData *regData);
void InitConfig_CONF2(max2769Config *config, max2769RegData *regData);
void InitConfig_CONF3(max2769Config *config, max2769RegData *regData);
void InitConfig_PLLCONF(max2769Config *config, max2769RegData *regData);
void InitConfig_DIV(max2769Config *config, max2769RegData *regData);
void InitConfig_FDIV(max2769Config *config, max2769RegData *regData);
void InitConfig_STRM(max2769Config *config, max2769RegData *regData);
void InitConfig_CLK(max2769Config *config, max2769RegData *regData);
/*
void Config_CONF1(BYTE *regPtr);
void Config_CONF2(BYTE *regPtr);
void Config_CONF3(BYTE *regPtr);
void Config_PLLCONF(BYTE *regPtr);
void Config_DIV(BYTE *regPtr);
void Config_FDIV(BYTE *regPtr);
void Config_STRM(BYTE *regPtr);
void Config_CLK(BYTE *regPtr);
*/
void SetBits_CONF1(max2769Config *config, max2769RegData *regData);

void SetBits_CONF2(max2769Config *config, max2769RegData *regData);
void SetBits_CONF3(max2769Config *config, max2769RegData *regData);
void SetBits_PLLCONF(max2769Config *config, max2769RegData *regData);
void SetBits_DIV(max2769Config *config, max2769RegData *regData);
void SetBits_FDIV(max2769Config *config, max2769RegData *regData);
void SetBits_STRM(max2769Config *config, max2769RegData *regData);
void SetBits_CLK(max2769Config *config, max2769RegData *regData);
void SetBits_TEST1(max2769Config *config, max2769RegData *regData);
void SetBits_TEST2(max2769Config *config, max2769RegData *regData);


void GetMAX2769_CONF1(BYTE *regPtr);
/*
void GetMAX2769_CONF2(BYTE *regPtr);
void GetMAX2769_CONF3(BYTE *regPtr);
void GetMAX2769_PLLCONF(BYTE *regPtr);
void GetMAX2769_DIV(BYTE *regPtr);
void GetMAX2769_FDIV(BYTE *regPtr);
void GetMAX2769_STRM(BYTE *regPtr);
void GetMAX2769_CLK(BYTE *regPtr);
void GetMAX2769_TEST1(BYTE *regPtr);
void GetMAX2769_TEST2(BYTE *regPtr);
*/

void DisplayMAX2769Config(max2769RegData regData);
void DisplayReg(BYTE *regPtr);

void SetRegisterData(regfield field, BYTE *regDat);
void SetRegisterData16(regfield16 field, BYTE *regDat);
void SetRegisterData32(regfield32 field, BYTE *regDat);

void SetRegisterBit(BYTE bit, BYTE loc, BYTE *regDat);
