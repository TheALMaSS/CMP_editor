#ifndef TEST_H
#define TEST_H

#include <vector>
#include <algorithm>

#define TEST_BASE 66300

enum testToDo {

    test_1A,

    test_1,

    test_1B,

    test_1C,

    test_3A,

    test_2,

    test_3B,

    test_3C,

    test_4,

    test_5,

    test_6

};

class test : public Crop {
public:
    bool Do(Farm* a_farm, LE* a_field, FarmEvent* a_ev);

    test(TTypesOfVegetation a_tov, TTypesOfCrops a_toc, Landscape* a_L)
        : Crop(a_tov, a_toc, a_L)
    {
        m_first_date = g_date->DayInYear(26, 8);
        SetUpFarmCategoryInformation();
    }
};

#endif