#include "../../Landscape/ls.h"
#include "../../Landscape/cropprogs/example.h"
#include "math.h"
#include <set>

bool example::Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev) {
    m_farm = a_farm;
    m_field = a_field;
    m_ev = a_ev;
    bool done = false;
    int daysLeft = 0;

    std::set<int> history;

    switch (m_ev->m_todo) {

    case example_start:
        a_field->ClearManagementActionSum();

        SimpleEvent(g_date->Date() + 0, END, false);
        break;

    case example_end:
        done = true;
        break;

    default:
        g_msg->Warn(WARN_BUG, "example::Do(): "
            "Unknown event type! ", "");
        exit(1);
    }

    return done;