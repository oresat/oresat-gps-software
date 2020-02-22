#include "controller.h"
#include "log_message.h"
#include "Tle.h"
#include "SGP4.h"
#include "Observer.h"
#include "CoordGeodetic.h"
#include "CoordTopocentric.h"
#include <systemd/sd-bus.h>
#include <thread>


#define DESTINATION     "org.OreSat.GPS"
#define INTERFACE_NAME  "org.OreSat.GPS"
#define OBJECT_PATH     "/org/OreSat/GPS"

static bool running = true;
static int current_state = Sleep;


static void dbus_thread(sd_bus * bus);


// ---------------------------------------------------------------------------
// sdbus vtable and callbacks


static int change_state_cb(
        sd_bus_message *m,
        void *userdata,
        sd_bus_error *ret_error) {

    int r;
    int32_t new_state;
    bool rv = true;

    r = sd_bus_message_read(m, "i", &new_state);
    if(r < 0)
        log_message(LOG_ERR, "Failed to parse parameters");

    rv = change_state((int)new_state);

    return sd_bus_reply_method_return(m, "b", rv);
}


// sd-bus handler callback used in vtable
static int sv_handler_cb(
        sd_bus *bus,
        const char *path,
        const char *interface,
        const char *property,
        sd_bus_message *reply,
        void *userdata,
        sd_bus_error *error) {

    StateVector *state_vector = (StateVector *)userdata;

    state_vector->sv_mutex.lock();

    sd_bus_message_append(
            reply,
            "((ddd)(ddd)i)",
            state_vector->position.x,
            state_vector->position.y,
            state_vector->position.z,
            state_vector->velocity.x,
            state_vector->velocity.y,
            state_vector->velocity.z,
            state_vector->time);

    state_vector->sv_mutex.unlock();

    return 1;
}


static const sd_bus_vtable vtable[] = {
    SD_BUS_VTABLE_START(0),
    SD_BUS_METHOD("ChangeState", "s", "b", change_state_cb, SD_BUS_VTABLE_UNPRIVILEGED),
    //SD_BUS_METHOD("NewTLE", "s", "b", new_TLE_cb, SD_BUS_VTABLE_UNPRIVILEGED),
    SD_BUS_PROPERTY("StateVector", "((ddd)(ddd)i)", sv_handler_cb, 0, SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
    //SD_BUS_PROPERTY("CurrentState", "i", sv_handler_cb, 0, SD_BUS_VTABLE_PROPERTY_EMITS_CHANGE),
    SD_BUS_VTABLE_END
};



// ---------------------------------------------------------------------------
// sdbus dbus



bool change_state(const int & new_state) {
    switch(current_state) {
        case Sleep :
            if(new_state == Sleep || new_state == SaveSignal || new_state == ParseTLE)
                current_state = new_state;
            else
                return false;
        case Error :
            if(new_state == Error || new_state == ParseTLE)
                current_state = new_state;
            else
                return false;
        case ParseTLE :
            if(new_state == ParseTLE || new_state == Error)
                current_state = new_state;
            else
                return false;
        case SaveSignal :
            if(new_state == SaveSignal || new_state == Error || new_state == ProcessSignal)
                current_state = new_state;
            else
                return false;
        case ProcessSignal :
            if(new_state == ProcessSignal || new_state == Sleep ||  new_state == Error || new_state == ParseTLE)
                current_state = new_state;
            else
                return false;
        default :
            return false;
    }
    return true;
}


int  gps_wrapper_main() {
    StateVector sv;
    sd_bus_slot * slot = NULL;
    sd_bus * bus = NULL;
    Tle tle = Tle("ISS (ZARYA)             ",
            "1 25544U 98067A   20052.93296053  .00002066  00000-0  45383-4 0  9997",
            "2 25544  51.6426 203.6800 0004732 301.4525 204.7455 15.49190254213992");
    SGP4 sgp4(tle);
    DateTime dt;
    dt.Now();
    Eci eci = sgp4.FindPosition(dt);
    Vector pos, vel;
    int r;

    // Connect to the bus
    r = sd_bus_open_system(&bus);
    if(r < 0)
        log_message(LOG_ERR, "Failed to connect to system bus.");

    // Take a well-known service name so that clients can find us
    r = sd_bus_request_name(bus, DESTINATION, SD_BUS_NAME_ALLOW_REPLACEMENT);
    if(r < 0)
        log_message(LOG_ERR, "Failed to acquire service name.");

    // Install the vtable
    r = sd_bus_add_object_vtable(
            bus,
            &slot,
            OBJECT_PATH,
            INTERFACE_NAME,
            vtable,
            &sv);
    if(r < 0)
        log_message(LOG_ERR, "Failed to add vtable.");

    // Start other thread
    std::thread dbus_thr(dbus_thread, bus);

    while(running) {
        switch(current_state) {
            case Sleep :
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            case Error :
                std::this_thread::sleep_for(std::chrono::milliseconds(500));
            case ParseTLE :
                dt.Now(); // get time
                eci = sgp4.FindPosition(dt);

                pos = eci.Position();
                sv.position.x = pos.x; sv.position.y = pos.y; sv.position.z = pos.z;

                vel = eci.Velocity();
                sv.velocity.x = vel.x; sv.velocity.y = vel.y; sv.velocity.z = vel.z;

                std::this_thread::sleep_for(std::chrono::seconds(1));
            case SaveSignal :
                std::this_thread::sleep_for(std::chrono::minutes(15)); // TODO signal dump from pru
                change_state(ProcessSignal);
            case ProcessSignal :
                std::this_thread::sleep_for(std::chrono::minutes(15)); // TODO call gnss-sdr
                change_state(ParseTLE);
            default :
                change_state(Error);
        }
    }

    // Stop other thread
    dbus_thr.join();

    r = sd_bus_release_name(bus, DESTINATION);
    if(r < 0)
        log_message(LOG_ERR, "Failed to release service name.");

    sd_bus_slot_unref(slot);
    sd_bus_unref(bus);

    return 0;
}


static void dbus_thread(sd_bus * bus) {
    int r;

    // loop forever and process dbus calls
    while(running) {
        // Process requests
        r = sd_bus_process(bus, NULL);
        if(r < 0)
            log_message(LOG_ERR, "Failed to process bus.");

        if (r > 0) // we processed a request, try to process another one, right-away
            continue;

        // Wait for the next request to process
        r = sd_bus_wait(bus, (uint64_t) -1);
        if(r < 0)
            log_message(LOG_ERR, "Failed to wait on bus.");
    }
}


