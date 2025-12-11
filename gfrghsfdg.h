#ifndef GFRGHSFDG_H
#define GFRGHSFDG_H

#include <vector>
#include <algorithm>

#define GFRGHSFDG_BASE 66300

enum gfrghsfdgToDo {
    gfrghsfdg_2,    gfrghsfdg_3,    gfrghsfdg_END,    gfrghsfdg_START};

class gfrghsfdg : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    gfrghsfdg(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(26, 8);
        SetUpFarmCategoryInformation();
    }
};

#endif