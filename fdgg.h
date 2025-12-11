#ifndef FDGG_H
#define FDGG_H

#include <vector>
#include <algorithm>

#define FDGG_BASE 66300

enum fdggToDo {

    fdgg_2,

    fdgg_3,

    fdgg_END,

    fdgg_START

};

class fdgg : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    fdgg(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = None;
        SetUpFarmCategoryInformation();
    }
};

#endif