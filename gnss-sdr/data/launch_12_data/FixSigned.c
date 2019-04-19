#include <stdio.h>

/* 
 * This will fix the launch 12 data into being two's complament.
 */

char fix_bits(char ch) {
    ch &= 0x3; //just incase
    if(ch == 0x3)
        ch = 0x2;
    else if(ch == 0x2)
        ch = 0x3;
    return ch;
}

char fix(char ch){
    //move to 1st two bits
    char a = ch & 0x3;
    char b = ((ch & 0xC) >> 2) & 0x3;
    char c = ((ch & 0x30) >> 4) & 0x3;
    char d = ((ch & 0xC0) >> 6) & 0x3;

    //fix
    a = fix_bits(a);
    b = fix_bits(b);
    c = fix_bits(c);
    d = fix_bits(d);

    //move back to location
    char rc = 0x0;
    rc |= a;
    rc |= (b << 2);
    rc |= (c << 4);
    rc |= (d << 6);

    return rc;
}


int main(int argv, char ** argc) {
    if(argv != 3) {
        printf("Missing Input\n");
        printf("./FILE INPUT_FILE_NAME OUTPUT_FILE_NAME\n");
        return 0;
    }


    FILE * aFile;
    aFile = fopen(argc[1],"r");
    if (aFile == NULL) {
        printf("INPUT FILE ERROR\n");
        return 0;
    }
    
    FILE * bFile;
    bFile = fopen(argc[2],"w");
    if (bFile == NULL) {
        printf("OUTPUT FILE ERROR\n");
        return 0;
    }

    int c;
    char fixed;
    while((c = fgetc(aFile)) != EOF) {
        fixed = fix((char)c);
        fputc(fixed, bFile);
    }

    fclose(aFile);
    fclose(bFile);

    return 1;
}
