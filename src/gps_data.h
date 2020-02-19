


struct GPS_ECEF_data {
    struct position {
        float x;
        float y;
        float z;
    };
    struct velocity {
        float x;
        float y;
        float z;
    };
    struct acceleration {
        float x;
        float y;
        float z;
    };
    //TODO time, UTC or GPS-UTC time???
};

// TODO struct GPS_LLA_data?
// TODO struct GPS_OSV_data?
