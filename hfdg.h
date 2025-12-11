#ifndef HFDG_H
#define HFDG_H

#include <vector>
#include <algorithm>

#define HFDG_BASE 66300

enum hfdgToDo {

    hfdg_2,

    hfdg_3,

    hfdg_END,

    hfdg_START

};

class hfdg : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    hfdg(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(01, 01);
        SetUpFarmCategoryInformation();
    }
};

#endif