#ifndef TEEEST_H
#define TEEEST_H

#include <vector>
#include <algorithm>

#define TEEEST_BASE 66300

enum teeestToDo {

    teeest_2,

    teeest_3,

    teeest_END,

    teeest_START

};

class teeest : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    teeest(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(1, 1);
        SetUpFarmCategoryInformation();
    }
};

#endif