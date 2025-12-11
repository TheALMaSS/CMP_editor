#include "../../Landscape/ls.h"
#include "../../Landscape/cropprogs/teeest.h"
#include "math.h"
#include <set>

bool teeest::Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev) {
    m_farm = a_farm;
    m_field = a_field;
    m_ev = a_ev;
    bool done = false;
    int daysLeft = 0;

    switch (m_ev->m_todo) {

    case teeest_start:
        a_field->ClearManagementActionSum();

        SimpleEvent(g_date->Date() + 0, teeest_1, false);
        break;

        
    case teeest_2:
        daysLeft = g_date->DayInYear(3, 5) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnRoll(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, teeest_2, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, teeest_END, false);
        break;
    
    case teeest_3:
        daysLeft = g_date->DayInYear(7, 7) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnSowWithFerti(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, teeest_3, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, teeest_END, false);
        break;
    
    case teeest_1:
        float myRand = g_rand_uni_fnc();

        if (myRand < 0.1) {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(1, 5)), teeest_2, false);
        }
        else {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(6, 6)), teeest_3, false);
        }

        break;

    case teeest_end:
        done = true;
        break;

    default:
        g_msg->Warn(WARN_BUG, "teeest::Do(): Unknown event type! ", "");
        exit(1);
    }

    return done;
}