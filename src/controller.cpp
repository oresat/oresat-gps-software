#include <systemd/sd-bus.h>
#include <thread>
#include "controller.h"
#include "log_message.h"


#define DESTINATION     "org.OreSat.GPS"
#define INTERFACE_NAME  "org.OreSat.GPS"
#define OBJECT_PATH     "/org/OreSat/GPS"

int gps_data_cb(sd_bus *bus,
                const char *path,
                const char *interface,
                const char *property,
                sd_bus_message *reply,
                void *userdata,
                sd_bus_error *ret_error){

    //TODO use this for property?

    return 1;
}

Controller::
Controller() : _ECEF_data() {
    int r;

    sd_bus_vtable vtable[] = {
        SD_BUS_VTABLE_START(0),
        SD_BUS_PROPERTY("GPS_ECEF_data", "{ddd}", NULL, 0, SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE), // only grabs position for now, TODO add rest of data later
        SD_BUS_VTABLE_END
    };

    /* Connect to the bus */
    r = sd_bus_open_system(&_bus);
    log_message(LOG_ERR, "Failed to connect to system bus.");

    /* Take a well-known service name so that clients can find us */
    r = sd_bus_request_name(_bus, DESTINATION, SD_BUS_NAME_ALLOW_REPLACEMENT);
    log_message(LOG_ERR, "Failed to acquire service name.\n");

    /* Install the vtable */
    r = sd_bus_add_object_vtable(_bus,
                                 &_slot,
                                 OBJECT_PATH,
                                 INTERFACE_NAME,
                                 vtable,
                                 &_ECEF_data);
    log_message(LOG_ERR, "Failed to add vtable.");
}


Controller::
~Controller() {
    int r = sd_bus_release_name(_bus, DESTINATION);
    log_message(LOG_ERR, "Failed to release service name.");

    sd_bus_slot_unref(_slot);
    sd_bus_unref(_bus);
}


int Controller::
run() { // TODO change to a thread
    int r;

    while(_running) {
        /* Process requests */
        r = sd_bus_process(_bus, NULL);
        log_message(LOG_ERR, "Failed to process bus.");

        if (r > 0) /* we processed a request, try to process another one, right-away */
            continue;

        /* Wait for the next request to process */
        r = sd_bus_wait(_bus, (uint64_t) -1);
        log_message(LOG_ERR, "Failed to wait on bus.");
    }

    return 1;
}


int Controller::
quit() {
    _running = false;
    return 1;
}
