#include <systemd/sd-bus.h>
#include <mutex>


struct XYZ {
    XYZ() : x(0.0), y(0.0), z(0.0) {};
    double x;
    double y;
    double z;
};


struct StateVector {
    StateVector() : time(0) {};
    XYZ position;
    XYZ velocity;
    int32_t time; // TODO UTC
    std::mutex sv_mutex;
};


enum states {
    Sleep = 0,
    Error = 1,
    ParseTLE = 2,
    SaveSignal = 3,
    ProcessSignal = 4,
};


bool change_state(const int & new_state);
int gps_wrapper_main();

