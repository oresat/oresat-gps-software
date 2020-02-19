

enum states {
    Sleep = 0,
    Error = 1,
    ParseTLE = 2,
    SaveSignals = 3,
    ProcessSignal = 4,
};


class StateMachine {
    public:
        StateMachine();
        ~StateMachine() = default;
        bool change_state(const int);
    private:
        int _current_state;
};
