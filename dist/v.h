#ifndef V_H
#define V_H

#include <vector>
#include <algorithm>

#define V_BASE 66300

enum vToDo {

    v_2,

    v_3,

    v_END,

    v_START

};

class v : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    v(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(10, 6);
        SetUpFarmCategoryInformation();
    }
};

#endif