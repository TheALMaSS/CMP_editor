#ifndef EXAMPLE_H
#define EXAMPLE_H

#include <vector>
#include <algorithm>

#define EXAMPLE_BASE 66300

enum exampleToDo {

    example_START,

    example_END

};

class example : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    example(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(26, 8);
        SetUpFarmCategoryInformation();
    }
};

#endif