#include "../../Landscape/ls.h"
#include "../../Landscape/cropprogs/fdgg.h"
#include "math.h"
#include <set>

bool fdgg::Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev) {
    m_farm = a_farm;
    m_field = a_field;
    m_ev = a_ev;
    bool done = false;
    int daysLeft = 0;

    switch (m_ev->m_todo) {

    case fdgg_start:
        a_field->ClearManagementActionSum();

        SimpleEvent(g_date->Date() + 0, fdgg_1, false);
        break;

        
    case fdgg_2:
        daysLeft = g_date->DayInYear(03, 05) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnRoll(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, fdgg_2, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, fdgg_END, false);
        break;
    
    case fdgg_3:
        daysLeft = g_date->DayInYear(07, 07) - g_date->DayInYear();
        if (daysLeft >= 0) {
            if (!m_farm->AutumnSowWithFerti(m_field, 0.0, daysLeft)) {
                    SimpleEvent(g_date->Date() + 1, fdgg_3, true);
                    break;
            }
        }

        SimpleEvent(g_date->Date() + 0, fdgg_END, false);
        break;
    
    case fdgg_1:
        float myRand = g_rand_uni_fnc();

        if (myRand < 0.1) {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(01, 05)), fdgg_2, false);
        }
        else {
            SimpleEvent(std::max(g_date->Date() + 1, g_date->OldDays() + g_date->DayInYear(06, 06)), fdgg_3, false);
        }

        break;

    case fdgg_end:
        done = true;
        break;

    default:
        g_msg->Warn(WARN_BUG, "fdgg::Do(): Unknown event type! ", "");
        exit(1);
    }

    return done;
}