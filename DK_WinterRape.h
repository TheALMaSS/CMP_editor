#ifndef DK_WINTER_RAPE_H
#define DK_WINTER_RAPE_H

#include <vector>
#include <algorithm>

#define DK_WINTER_RAPE_BASE 66300

enum DK_WinterRapeToDo {

    dk_winter_rape_1A,

    dk_winter_rape_1,

    dk_winter_rape_1B,

    dk_winter_rape_1C,

    dk_winter_rape_3A,

    dk_winter_rape_2,

    dk_winter_rape_3B,

    dk_winter_rape_3C,

    dk_winter_rape_4,

    dk_winter_rape_5,

    dk_winter_rape_6

};

class DK_WinterRape : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    DK_WinterRape(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(26, 8);
        SetUpFarmCategoryInformation();
    }
};

#endif