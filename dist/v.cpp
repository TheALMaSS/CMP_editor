#include "../../Landscape/ls.h"
#include "../../Landscape/cropprogs/v.h"
#include "math.h"
#include <set>

bool v::Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev) {
    m_farm = a_farm;
    m_field = a_field;
    m_ev = a_ev;
    bool done = false;
    int daysLeft = 0;

    switch (m_ev->m_todo) {

    case v_start:
        a_field->ClearManagementActionSum();

        SimpleEvent(g_date->Date() + 0, v_1, false);
        break;

        
    case v_2:
        daysLeft = g_date->DayInYear(3, 5) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnRoll(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, v_2, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, v_END, false);
        break;
    
    case v_3:
        daysLeft = g_date->DayInYear(7, 7) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnSowWithFerti(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, v_3, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, v_END, false);
        break;
    
    case v_1:
        float myRand = g_rand_uni_fnc();

        if (myRand < 0.1) {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(1, 5)), v_2, false);
        }
        else {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(6, 6)), v_3, false);
        }

        break;

    case v_end:
        done = true;
        break;

    default:
        g_msg->Warn(WARN_BUG, "v::Do(): Unknown event type! ", "");
        exit(1);
    }

    return done;
}