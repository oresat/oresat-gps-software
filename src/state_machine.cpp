#include <iostream>
#include "state_machine.h"

StateMachine::
StateMachine() {
    _current_state = Sleep;
}

bool StateMachine::
change_state(const int new_state) {
    switch(_current_state) {
        case Sleep :
            if(new_state == Sleep || new_state == SaveSignals || new_state == ParseTLE)
                _current_state = new_state;
            else
                return false;
        case Error :
            if(new_state == Error || new_state == ParseTLE)
                _current_state = new_state;
            else
                return false;
        case ParseTLE :
            if(new_state == ParseTLE || new_state == Error)
                _current_state = new_state;
            else
                return false;
        case SaveSignals :
            if(new_state == SaveSignals || new_state == Error || new_state == ProcessSignal)
                _current_state = new_state;
            else
                return false;
        case ProcessSignal :
            if(new_state == ProcessSignal || new_state == Sleep ||  new_state == Error || new_state == ParseTLE)
                _current_state = new_state;
            else
                return false;
        default :
            return false;
    }
    return true;
}
