#include <mutex>
#include <systemd/sd-bus.h>
#include "state_machine.h"
#include "gps_data.h"




/*
 * Dbus interface and main class for controlling gps process/daemon.
 */
class Controller {
    public:
        Controller();
        ~Controller();
        int run();
        int quit();

    private:
        int _running;
        StateMachine _state_machine;
        GPS_ECEF_data _ECEF_data;
        sd_bus_slot * _slot;
        sd_bus * _bus;
        std::mutex controller_mutex;
};



