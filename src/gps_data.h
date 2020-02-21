
struct XYZ {
    float x;
    float y;
    float z;
};


struct GPS_ECEF_data {
    XYZ position;
    XYZ velocity;
    XYZ acceleration;
    //TODO time, UTC or GPS-UTC time???
};

// TODO struct GPS_LLA_data?
// TODO struct GPS_OSV_data?
