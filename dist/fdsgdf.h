#ifndef FDSGDF_H
#define FDSGDF_H

#include <vector>
#include <algorithm>

#define FDSGDF_BASE 66300

enum fdsgdfToDo {

    fdsgdf_2,

    fdsgdf_3,

    fdsgdf_END,

    fdsgdf_START

};

class fdsgdf : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    fdsgdf(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = None;
        SetUpFarmCategoryInformation();
    }
};

#endif